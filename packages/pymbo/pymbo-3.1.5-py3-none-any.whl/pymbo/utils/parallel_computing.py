"""
Parallel Computing Module for PyMBO
High-performance parallel processing for Bayesian optimization operations
"""

import multiprocessing as mp
from multiprocessing import Pool, Manager, Queue, Process, Value, Array
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import time
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np
import torch
from functools import partial
import joblib
from joblib import Parallel, delayed
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ParallelConfig:
    """Configuration for parallel processing"""
    n_workers: int = None
    backend: str = "thread"  # "thread", "process", "joblib"
    chunk_size: int = None
    memory_limit_mb: int = 1000
    timeout_seconds: int = 300

class ParallelGPProcessor:
    """Parallel processor for Gaussian Process operations"""
    
    def __init__(self, config: ParallelConfig = None):
        """
        Initialize parallel GP processor
        
        Args:
            config: Parallel processing configuration
        """
        self.config = config or ParallelConfig()
        
        # Auto-detect optimal number of workers
        if self.config.n_workers is None:
            self.config.n_workers = min(mp.cpu_count(), 8)  # Cap at 8 to avoid overhead
        
        # Auto-detect optimal chunk size
        if self.config.chunk_size is None:
            self.config.chunk_size = max(1, 100 // self.config.n_workers)
        
        logger.info(f"ParallelGPProcessor initialized: {self.config.n_workers} workers, "
                   f"backend: {self.config.backend}, chunk_size: {self.config.chunk_size}")
    
    def parallel_model_fitting(
        self,
        data_list: List[Tuple[np.ndarray, np.ndarray]],
        kernel_params_list: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Fit multiple GP models in parallel
        
        Args:
            data_list: List of (X, y) training data tuples
            kernel_params_list: List of kernel parameter dictionaries
            progress_callback: Optional progress callback
            
        Returns:
            List of fitted model parameters
        """
        total_models = len(data_list)
        
        if self.config.backend == "joblib":
            return self._parallel_fitting_joblib(
                data_list, kernel_params_list, progress_callback
            )
        elif self.config.backend == "process":
            return self._parallel_fitting_process(
                data_list, kernel_params_list, progress_callback
            )
        else:  # thread
            return self._parallel_fitting_thread(
                data_list, kernel_params_list, progress_callback
            )
    
    def _parallel_fitting_joblib(
        self,
        data_list: List[Tuple[np.ndarray, np.ndarray]],
        kernel_params_list: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """Fit models using joblib parallel processing"""
        
        def fit_single_model(data_params_tuple):
            """Fit a single GP model"""
            try:
                (X, y), params = data_params_tuple
                return _fit_gp_model_sklearn(X, y, params)
            except Exception as e:
                logger.error(f"Error fitting model: {e}")
                return None
        
        # Use joblib for parallel processing
        results = Parallel(
            n_jobs=self.config.n_workers,
            backend='threading',
            verbose=1 if progress_callback else 0
        )(
            delayed(fit_single_model)(data_params) 
            for data_params in zip(data_list, kernel_params_list)
        )
        
        return results
    
    def _parallel_fitting_process(
        self,
        data_list: List[Tuple[np.ndarray, np.ndarray]],
        kernel_params_list: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """Fit models using process pool"""
        
        with ProcessPoolExecutor(max_workers=self.config.n_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(_fit_gp_model_sklearn, X, y, params): i
                for i, ((X, y), params) in enumerate(zip(data_list, kernel_params_list))
            }
            
            results = [None] * len(data_list)
            completed = 0
            
            # Collect results as they complete
            for future in as_completed(future_to_index, timeout=self.config.timeout_seconds):
                index = future_to_index[future]
                try:
                    result = future.result()
                    results[index] = result
                    completed += 1
                    
                    if progress_callback:
                        progress_callback(completed, len(data_list))
                        
                except Exception as e:
                    logger.error(f"Model fitting failed for index {index}: {e}")
                    results[index] = None
                    completed += 1
        
        return results
    
    def _parallel_fitting_thread(
        self,
        data_list: List[Tuple[np.ndarray, np.ndarray]],
        kernel_params_list: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """Fit models using thread pool"""
        
        with ThreadPoolExecutor(max_workers=self.config.n_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(_fit_gp_model_sklearn, X, y, params): i
                for i, ((X, y), params) in enumerate(zip(data_list, kernel_params_list))
            }
            
            results = [None] * len(data_list)
            completed = 0
            
            # Collect results as they complete
            for future in as_completed(future_to_index, timeout=self.config.timeout_seconds):
                index = future_to_index[future]
                try:
                    result = future.result()
                    results[index] = result
                    completed += 1
                    
                    if progress_callback:
                        progress_callback(completed, len(data_list))
                        
                except Exception as e:
                    logger.error(f"Model fitting failed for index {index}: {e}")
                    results[index] = None
                    completed += 1
        
        return results
    
    def parallel_acquisition_optimization(
        self,
        acquisition_func: Callable,
        bounds: np.ndarray,
        num_candidates: int = 100,
        num_restarts: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Optimize acquisition function in parallel with multiple restarts
        
        Args:
            acquisition_func: Acquisition function to optimize
            bounds: Parameter bounds [2, d] (min, max)
            num_candidates: Number of candidate points to evaluate
            num_restarts: Number of optimization restarts
            
        Returns:
            Tuple of (best_candidates, best_values)
        """
        
        def optimize_single_restart(restart_idx):
            """Single restart optimization"""
            try:
                # Generate random starting point
                np.random.seed(restart_idx)  # Reproducible restarts
                d = bounds.shape[1]
                start_point = bounds[0] + np.random.random(d) * (bounds[1] - bounds[0])
                
                # Simple gradient-free optimization (can be replaced with scipy.optimize)
                best_x = start_point.copy()
                best_val = acquisition_func(best_x.reshape(1, -1))
                
                # Random search with local refinement
                for _ in range(20):
                    # Small perturbation around current best
                    noise = np.random.normal(0, 0.1, d)
                    candidate = np.clip(best_x + noise, bounds[0], bounds[1])
                    val = acquisition_func(candidate.reshape(1, -1))
                    
                    if val > best_val:
                        best_x = candidate
                        best_val = val
                
                return best_x, best_val
                
            except Exception as e:
                logger.error(f"Error in restart {restart_idx}: {e}")
                return None, -np.inf
        
        # Run optimization restarts in parallel
        if self.config.backend == "joblib":
            results = Parallel(n_jobs=self.config.n_workers)(
                delayed(optimize_single_restart)(i) for i in range(num_restarts)
            )
        else:
            with ThreadPoolExecutor(max_workers=self.config.n_workers) as executor:
                results = list(executor.map(optimize_single_restart, range(num_restarts)))
        
        # Find best result
        valid_results = [(x, val) for x, val in results if x is not None]
        if not valid_results:
            # Fallback to random point
            d = bounds.shape[1]
            random_x = bounds[0] + np.random.random(d) * (bounds[1] - bounds[0])
            return random_x.reshape(1, -1), np.array([0.0])
        
        best_x, best_val = max(valid_results, key=lambda item: item[1])
        return best_x.reshape(1, -1), np.array([best_val])
    
    def parallel_cross_validation(
        self,
        X: np.ndarray,
        y: np.ndarray,
        kernel_params_list: List[Dict[str, Any]],
        cv_folds: int = 5
    ) -> List[Dict[str, float]]:
        """
        Perform parallel cross-validation for hyperparameter selection
        
        Args:
            X: Input data
            y: Target values
            kernel_params_list: List of kernel parameter sets to evaluate
            cv_folds: Number of cross-validation folds
            
        Returns:
            List of CV scores for each parameter set
        """
        
        def evaluate_params(params):
            """Evaluate a single parameter set using CV"""
            try:
                from sklearn.model_selection import cross_val_score
                from sklearn.gaussian_process import GaussianProcessRegressor
                from sklearn.gaussian_process.kernels import RBF, Matern, WhiteKernel
                
                # Create GP with given parameters
                length_scale = params.get('length_scale', 1.0)
                nu = params.get('nu', 2.5)
                alpha = params.get('alpha', 1e-6)
                
                if nu == 2.5:
                    kernel = Matern(length_scale=length_scale, nu=nu) + WhiteKernel(noise_level=alpha)
                else:
                    kernel = RBF(length_scale=length_scale) + WhiteKernel(noise_level=alpha)
                
                gp = GaussianProcessRegressor(
                    kernel=kernel,
                    n_restarts_optimizer=2,
                    alpha=alpha
                )
                
                # Perform cross-validation
                scores = cross_val_score(gp, X, y, cv=cv_folds, scoring='neg_mean_squared_error')
                
                return {
                    'params': params,
                    'mean_score': np.mean(scores),
                    'std_score': np.std(scores),
                    'scores': scores.tolist()
                }
                
            except Exception as e:
                logger.error(f"Error in CV evaluation: {e}")
                return {
                    'params': params,
                    'mean_score': -np.inf,
                    'std_score': np.inf,
                    'scores': []
                }
        
        # Run CV in parallel
        if self.config.backend == "joblib":
            results = Parallel(n_jobs=self.config.n_workers)(
                delayed(evaluate_params)(params) for params in kernel_params_list
            )
        else:
            with ThreadPoolExecutor(max_workers=self.config.n_workers) as executor:
                results = list(executor.map(evaluate_params, kernel_params_list))
        
        return results

class AsyncParallelManager:
    """Manage asynchronous parallel operations"""
    
    def __init__(self, max_concurrent: int = 4):
        """
        Initialize async parallel manager
        
        Args:
            max_concurrent: Maximum number of concurrent operations
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_tasks = set()
        
        logger.info(f"AsyncParallelManager initialized with {max_concurrent} max concurrent operations")
    
    async def run_parallel_async(
        self,
        tasks: List[Callable],
        *args,
        progress_callback: Optional[Callable] = None,
        **kwargs
    ) -> List[Any]:
        """
        Run multiple tasks in parallel asynchronously
        
        Args:
            tasks: List of callable tasks
            progress_callback: Optional progress callback
            *args, **kwargs: Arguments passed to tasks
            
        Returns:
            List of task results
        """
        
        async def run_single_task(task_func, task_idx):
            """Run a single task with semaphore control"""
            async with self.semaphore:
                try:
                    # Run task in thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, task_func, *args, **kwargs)
                    
                    if progress_callback:
                        progress_callback(task_idx + 1, len(tasks))
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Task {task_idx} failed: {e}")
                    return None
        
        # Create and run all tasks
        task_coroutines = [
            run_single_task(task, i) for i, task in enumerate(tasks)
        ]
        
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Filter out exceptions and return results
        return [r for r in results if not isinstance(r, Exception)]

class ParallelHyperparameterOptimizer:
    """Parallel hyperparameter optimization for GP models"""
    
    def __init__(self, config: ParallelConfig = None):
        """
        Initialize parallel hyperparameter optimizer
        
        Args:
            config: Parallel processing configuration
        """
        self.config = config or ParallelConfig()
        self.gp_processor = ParallelGPProcessor(config)
        
    def optimize_hyperparameters(
        self,
        X: np.ndarray,
        y: np.ndarray,
        param_grid: Dict[str, List[Any]],
        cv_folds: int = 5,
        scoring: str = 'neg_mean_squared_error'
    ) -> Dict[str, Any]:
        """
        Optimize GP hyperparameters using parallel grid search with CV
        
        Args:
            X: Input data
            y: Target values
            param_grid: Parameter grid to search
            cv_folds: Number of CV folds
            scoring: Scoring metric
            
        Returns:
            Best parameters and CV score
        """
        from sklearn.model_selection import ParameterGrid
        
        # Generate all parameter combinations
        param_combinations = list(ParameterGrid(param_grid))
        
        logger.info(f"Optimizing hyperparameters: {len(param_combinations)} combinations")
        
        # Evaluate parameters in parallel
        cv_results = self.gp_processor.parallel_cross_validation(
            X, y, param_combinations, cv_folds
        )
        
        # Find best parameters
        best_result = max(cv_results, key=lambda x: x['mean_score'])
        
        logger.info(f"Best hyperparameters found: {best_result['params']} "
                   f"(CV score: {best_result['mean_score']:.4f})")
        
        return best_result

# Utility functions for parallel processing

def _fit_gp_model_sklearn(X: np.ndarray, y: np.ndarray, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fit a single GP model using scikit-learn (for multiprocessing)
    
    Args:
        X: Input data
        y: Target values
        params: Model parameters
        
    Returns:
        Fitted model parameters
    """
    try:
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import RBF, Matern, WhiteKernel
        
        # Extract parameters
        length_scale = params.get('length_scale', 1.0)
        nu = params.get('nu', 2.5)
        alpha = params.get('alpha', 1e-6)
        
        # Create kernel
        if nu == 2.5:
            kernel = Matern(length_scale=length_scale, nu=nu) + WhiteKernel(noise_level=alpha)
        else:
            kernel = RBF(length_scale=length_scale) + WhiteKernel(noise_level=alpha)
        
        # Create and fit GP
        gp = GaussianProcessRegressor(
            kernel=kernel,
            n_restarts_optimizer=3,
            alpha=alpha,
            normalize_y=True
        )
        
        gp.fit(X, y)
        
        # Return fitted parameters
        return {
            'model': gp,
            'kernel_params': {
                'length_scale': gp.kernel_.k1.length_scale,
                'nu': nu,
                'alpha': gp.alpha
            },
            'log_marginal_likelihood': gp.log_marginal_likelihood_value_,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error fitting GP model: {e}")
        return {
            'model': None,
            'kernel_params': params,
            'log_marginal_likelihood': -np.inf,
            'success': False,
            'error': str(e)
        }

def parallel_matrix_operations(
    matrices: List[np.ndarray],
    operation: str,
    n_workers: int = None
) -> List[np.ndarray]:
    """
    Perform matrix operations in parallel
    
    Args:
        matrices: List of matrices
        operation: Operation to perform ('cholesky', 'inverse', 'det')
        n_workers: Number of workers
        
    Returns:
        List of operation results
    """
    if n_workers is None:
        n_workers = min(mp.cpu_count(), len(matrices))
    
    def apply_operation(matrix):
        """Apply operation to a single matrix"""
        try:
            if operation == 'cholesky':
                return np.linalg.cholesky(matrix)
            elif operation == 'inverse':
                return np.linalg.inv(matrix)
            elif operation == 'det':
                return np.linalg.det(matrix)
            else:
                raise ValueError(f"Unknown operation: {operation}")
        except Exception as e:
            logger.error(f"Matrix operation failed: {e}")
            return None
    
    # Use joblib for parallel processing
    results = Parallel(n_jobs=n_workers)(
        delayed(apply_operation)(matrix) for matrix in matrices
    )
    
    return results

# Global instances
default_config = ParallelConfig()
parallel_gp_processor = ParallelGPProcessor(default_config)
async_manager = AsyncParallelManager()
hyperparameter_optimizer = ParallelHyperparameterOptimizer(default_config)

__all__ = [
    'ParallelConfig', 'ParallelGPProcessor', 'AsyncParallelManager',
    'ParallelHyperparameterOptimizer', 'parallel_matrix_operations',
    'parallel_gp_processor', 'async_manager', 'hyperparameter_optimizer'
]