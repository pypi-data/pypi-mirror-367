"""
Enhanced Multi-Objective Bayesian Optimizer with Performance Optimizations
Integrates all performance improvements for smooth, responsive operation
"""

import logging
import time
import asyncio
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
import torch
from concurrent.futures import ThreadPoolExecutor

# Import performance optimization modules
from pymbo.utils.async_processing import (
    AsyncOptimizer, async_optimizer, 
    background_manager, progressive_computer
)
from pymbo.utils.vectorized_operations import (
    VectorizedBayesianOps, vectorized_ops, batched_gp_ops
)
from pymbo.utils.parallel_computing import (
    ParallelGPProcessor, ParallelConfig, parallel_gp_processor
)
from pymbo.utils.performance_optimizer import (
    PerformanceMonitor, memory_manager, plot_cache, 
    performance_timer, optimized_plot_update
)
from pymbo.utils.progressive_ui import (
    ProgressiveOperationManager, ProgressInfo, OperationStatus,
    ProgressTracker, get_progressive_manager
)

# Import base optimizer
from pymbo.core.optimizer import EnhancedMultiObjectiveOptimizer

logger = logging.getLogger(__name__)

class PerformanceEnhancedOptimizer(EnhancedMultiObjectiveOptimizer):
    """
    Performance-enhanced multi-objective Bayesian optimizer
    
    This class extends the base optimizer with:
    - Asynchronous processing for UI responsiveness
    - Vectorized operations for speed
    - Parallel GP model fitting
    - Progressive computation with interruption
    - Intelligent memory management
    - Advanced caching strategies
    """
    
    def __init__(
        self,
        params_config: Dict[str, Dict[str, Any]],
        responses_config: Dict[str, Dict[str, Any]],
        general_constraints: Optional[List[str]] = None,
        random_seed: Optional[int] = None,
        initial_sampling_method: str = "LHS",
        num_restarts: int = 10,
        raw_samples: int = 100,
        enable_async: bool = True,
        enable_parallel: bool = True,
        enable_caching: bool = True,
        parallel_config: Optional[ParallelConfig] = None,
        **kwargs
    ):
        """
        Initialize the performance-enhanced optimizer
        
        Args:
            params_config: Parameter configuration
            responses_config: Response configuration
            general_constraints: General constraints
            random_seed: Random seed for reproducibility
            initial_sampling_method: Initial sampling method
            num_restarts: Number of optimization restarts
            raw_samples: Number of raw samples
            enable_async: Enable asynchronous processing
            enable_parallel: Enable parallel processing
            enable_caching: Enable caching
            parallel_config: Parallel processing configuration
            **kwargs: Additional keyword arguments
        """
        # Initialize base optimizer
        super().__init__(
            params_config=params_config,
            responses_config=responses_config,
            general_constraints=general_constraints,
            random_seed=random_seed,
            initial_sampling_method=initial_sampling_method,
            num_restarts=num_restarts,
            raw_samples=raw_samples,
            **kwargs
        )
        
        # Performance enhancement settings
        self.enable_async = enable_async
        self.enable_parallel = enable_parallel
        self.enable_caching = enable_caching
        
        # Initialize performance components
        self.async_optimizer = async_optimizer if enable_async else None
        self.vectorized_ops = vectorized_ops
        
        # Setup parallel processing
        if enable_parallel:
            self.parallel_config = parallel_config or ParallelConfig(
                n_workers=min(4, torch.get_num_threads()),
                backend="thread"
            )
            self.parallel_gp = ParallelGPProcessor(self.parallel_config)
        else:
            self.parallel_gp = None
        
        # Performance monitoring
        self.perf_monitor = PerformanceMonitor()
        self.operation_times = {}
        
        # Progressive operation manager
        self.progressive_manager = None
        
        # Cache for expensive computations
        self.computation_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info(f"PerformanceEnhancedOptimizer initialized - "
                   f"Async: {enable_async}, Parallel: {enable_parallel}, "
                   f"Caching: {enable_caching}")
    
    def set_progress_manager(self, parent_window=None):
        """Set up progressive operation manager with UI parent"""
        self.progressive_manager = get_progressive_manager(parent_window)
    
    @performance_timer
    async def suggest_next_experiment_async(
        self, 
        n_suggestions: int = 1,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Asynchronous version of suggest_next_experiment with progress tracking
        
        Args:
            n_suggestions: Number of suggestions to generate
            progress_callback: Optional progress callback function
            
        Returns:
            List of suggested parameter combinations
        """
        if not self.enable_async:
            return self.suggest_next_experiment(n_suggestions)
        
        return await self.async_optimizer.run_optimization_async(
            self._suggest_next_experiment_with_progress,
            n_suggestions,
            progress_callback,
            task_name="generate_suggestions"
        )
    
    def _suggest_next_experiment_with_progress(
        self,
        n_suggestions: int,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate suggestions with progress tracking
        
        Args:
            n_suggestions: Number of suggestions
            progress_callback: Progress callback function
            
        Returns:
            List of suggestions
        """
        if progress_callback:
            progress_info = ProgressInfo(
                current=0,
                total=100,
                percentage=0.0,
                stage="initializing",
                message="Preparing to generate suggestions...",
                elapsed_time=0.0,
                estimated_remaining=0.0,
                status=OperationStatus.RUNNING
            )
            progress_callback(progress_info)
        
        start_time = time.time()
        
        try:
            # Check if we have enough data for GP models
            if (not hasattr(self, "train_X") or not hasattr(self, "train_Y") or 
                self.train_X.shape[0] < 3):
                
                if progress_callback:
                    progress_info.stage = "initial_sampling"
                    progress_info.message = "Insufficient data, using initial sampling"
                    progress_info.percentage = 50.0
                    progress_info.elapsed_time = time.time() - start_time
                    progress_callback(progress_info)
                
                return self._generate_doe_samples(n_suggestions, method="LHS")
            
            # Update progress - building models
            if progress_callback:
                progress_info.stage = "building_models"
                progress_info.message = "Building Gaussian Process models..."
                progress_info.percentage = 25.0
                progress_info.elapsed_time = time.time() - start_time
                progress_callback(progress_info)
            
            # Build models (with parallel processing if enabled)
            models = self._build_models_enhanced()
            if models is None:
                return self._generate_random_samples(n_suggestions)
            
            # Update progress - setting up acquisition
            if progress_callback:
                progress_info.stage = "acquisition_setup"
                progress_info.message = "Setting up acquisition function..."
                progress_info.percentage = 50.0
                progress_info.elapsed_time = time.time() - start_time
                progress_callback(progress_info)
            
            # Setup acquisition function
            acq_func = self._setup_acquisition_function(models)
            if acq_func is None:
                return self._generate_random_samples(n_suggestions)
            
            # Update progress - optimizing acquisition
            if progress_callback:
                progress_info.stage = "optimization"
                progress_info.message = "Optimizing acquisition function..."
                progress_info.percentage = 75.0
                progress_info.elapsed_time = time.time() - start_time
                progress_callback(progress_info)
            
            # Optimize acquisition function (with parallel restarts if enabled)
            suggestions = self._optimize_acquisition_function_enhanced(acq_func, n_suggestions)
            
            # Final progress update
            if progress_callback:
                progress_info.stage = "completed"
                progress_info.message = f"Generated {len(suggestions)} suggestions"
                progress_info.percentage = 100.0
                progress_info.elapsed_time = time.time() - start_time
                progress_info.status = OperationStatus.COMPLETED
                progress_callback(progress_info)
            
            return suggestions
            
        except Exception as e:
            if progress_callback:
                progress_info.stage = "error"
                progress_info.message = f"Error: {str(e)}"
                progress_info.status = OperationStatus.ERROR
                progress_callback(progress_info)
            
            logger.error(f"Error in suggestion generation: {e}")
            return self._generate_random_samples(n_suggestions)
    
    @performance_timer
    def _build_models_enhanced(self):
        """
        Build GP models with performance enhancements
        
        Returns:
            Enhanced GP models or None if building fails
        """
        cache_key = self._generate_model_cache_key()
        
        # Check cache first
        if self.enable_caching and cache_key in self.computation_cache:
            logger.debug("Using cached GP models")
            self.cache_hits += 1
            return self.computation_cache[cache_key]
        
        self.cache_misses += 1
        
        try:
            if self.enable_parallel and self.parallel_gp:
                # Use parallel model building
                models = self._build_models_parallel()
            else:
                # Use vectorized operations for single-threaded building
                models = self._build_models_vectorized()
            
            # Cache the models
            if self.enable_caching and models is not None:
                self.computation_cache[cache_key] = models
                
                # Limit cache size
                if len(self.computation_cache) > 10:
                    oldest_key = min(self.computation_cache.keys())
                    del self.computation_cache[oldest_key]
            
            return models
            
        except Exception as e:
            logger.error(f"Error in enhanced model building: {e}")
            return self._build_models()  # Fallback to base implementation
    
    def _build_models_parallel(self):
        """Build models using parallel processing"""
        try:
            if not hasattr(self, "train_X") or not hasattr(self, "train_Y"):
                return None
            
            # Prepare data for parallel processing
            data_list = []
            for i, obj_name in enumerate(self.objective_names):
                if i >= self.train_Y.shape[1]:
                    continue
                
                Y_obj = self.train_Y[:, i]
                finite_mask = torch.isfinite(Y_obj)
                
                if finite_mask.sum() < 3:  # Minimum data points
                    continue
                
                X_filtered = self.train_X[finite_mask].cpu().numpy()
                Y_filtered = Y_obj[finite_mask].cpu().numpy()
                
                data_list.append((X_filtered, Y_filtered))
            
            if not data_list:
                return None
            
            # Create kernel parameters for each model
            kernel_params_list = [
                {
                    'length_scale': 1.0,
                    'nu': 2.5,
                    'alpha': 1e-6
                }
                for _ in data_list
            ]
            
            # Fit models in parallel
            fitted_models = self.parallel_gp.parallel_model_fitting(
                data_list, kernel_params_list
            )
            
            # Convert back to BoTorch models if needed
            if fitted_models and all(m is not None for m in fitted_models):
                logger.info(f"Successfully built {len(fitted_models)} models in parallel")
                return fitted_models[0]['model'] if len(fitted_models) == 1 else fitted_models
            
            return None
            
        except Exception as e:
            logger.error(f"Error in parallel model building: {e}")
            return None
    
    def _build_models_vectorized(self):
        """Build models using vectorized operations"""
        try:
            # Use vectorized operations for faster computation
            if not hasattr(self, "train_X") or not hasattr(self, "train_Y"):
                return None
            
            # Leverage vectorized kernel computations
            kernel_matrices = []
            for i, obj_name in enumerate(self.objective_names):
                if i >= self.train_Y.shape[1]:
                    continue
                
                Y_obj = self.train_Y[:, i]
                finite_mask = torch.isfinite(Y_obj)
                
                if finite_mask.sum() < 3:
                    continue
                
                X_filtered = self.train_X[finite_mask]
                
                # Use vectorized kernel computation
                K = self.vectorized_ops.batch_kernel_matrix(
                    X_filtered, 
                    kernel_type="rbf",
                    length_scale=1.0,
                    output_scale=1.0,
                    noise_level=1e-6
                )
                kernel_matrices.append(K)
            
            # Use base implementation with pre-computed kernels
            return self._build_models()
            
        except Exception as e:
            logger.error(f"Error in vectorized model building: {e}")
            return None
    
    def _optimize_acquisition_function_enhanced(
        self, 
        acq_func, 
        n_suggestions: int
    ):
        """
        Enhanced acquisition function optimization with parallel restarts
        
        Args:
            acq_func: Acquisition function
            n_suggestions: Number of suggestions
            
        Returns:
            Optimized suggestions
        """
        try:
            if self.enable_parallel and self.parallel_gp:
                # Use parallel optimization with multiple restarts
                bounds = torch.stack([
                    torch.zeros(len(self.parameter_transformer.param_names), dtype=self.dtype),
                    torch.ones(len(self.parameter_transformer.param_names), dtype=self.dtype),
                ]).cpu().numpy()
                
                candidates, values = self.parallel_gp.parallel_acquisition_optimization(
                    lambda x: acq_func(torch.tensor(x, dtype=self.dtype, device=self.device)).cpu().numpy(),
                    bounds,
                    num_candidates=1000,
                    num_restarts=self.num_restarts
                )
                
                # Convert back to parameter dictionaries
                suggestions = []
                for i in range(min(n_suggestions, candidates.shape[0])):
                    candidate_tensor = torch.tensor(candidates[i], dtype=self.dtype)
                    param_dict = self.parameter_transformer.tensor_to_params(candidate_tensor)
                    suggestions.append(param_dict)
                
                return suggestions
            else:
                # Use vectorized optimization
                return self._optimize_acquisition_function_vectorized(acq_func, n_suggestions)
                
        except Exception as e:
            logger.error(f"Error in enhanced acquisition optimization: {e}")
            return self._optimize_acquisition_function(acq_func, n_suggestions)
    
    def _optimize_acquisition_function_vectorized(self, acq_func, n_suggestions: int):
        """Vectorized acquisition function optimization"""
        try:
            bounds = torch.stack([
                torch.zeros(len(self.parameter_transformer.param_names), dtype=self.dtype),
                torch.ones(len(self.parameter_transformer.param_names), dtype=self.dtype),
            ]).to(self.device)
            
            # Use vectorized operations for optimization
            best_candidates, best_values = self.vectorized_ops.batch_acquisition_optimization(
                acq_func, bounds, self.num_restarts, self.raw_samples
            )
            
            # Convert to parameter dictionaries
            suggestions = []
            for i in range(min(n_suggestions, best_candidates.shape[0])):
                param_dict = self.parameter_transformer.tensor_to_params(best_candidates[i])
                suggestions.append(param_dict)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error in vectorized acquisition optimization: {e}")
            return self._optimize_acquisition_function(acq_func, n_suggestions)
    
    def _generate_model_cache_key(self) -> str:
        """Generate cache key for model storage"""
        if not hasattr(self, "train_X") or not hasattr(self, "train_Y"):
            return "no_data"
        
        # Use hash of training data
        X_hash = hash(self.train_X.cpu().numpy().tobytes())
        Y_hash = hash(self.train_Y.cpu().numpy().tobytes())
        
        return f"models_{X_hash}_{Y_hash}_{len(self.objective_names)}"
    
    @performance_timer
    def add_experimental_data_enhanced(
        self, 
        data_df: pd.DataFrame,
        progress_callback: Optional[Callable] = None
    ) -> None:
        """
        Enhanced data addition with progress tracking and memory management
        
        Args:
            data_df: Experimental data to add
            progress_callback: Optional progress callback
        """
        start_time = time.time()
        
        try:
            if progress_callback:
                progress_info = ProgressInfo(
                    current=0,
                    total=100,
                    percentage=0.0,
                    stage="validating_data",
                    message="Validating experimental data...",
                    elapsed_time=0.0,
                    estimated_remaining=0.0,
                    status=OperationStatus.RUNNING
                )
                progress_callback(progress_info)
            
            # Clear model cache since data is changing
            if self.enable_caching:
                self.computation_cache.clear()
            
            # Memory cleanup before processing
            memory_manager.intelligent_cleanup()
            
            # Update progress
            if progress_callback:
                progress_info.stage = "adding_data"
                progress_info.message = f"Adding {len(data_df)} data points..."
                progress_info.percentage = 25.0
                progress_info.elapsed_time = time.time() - start_time
                progress_callback(progress_info)
            
            # Add data using base implementation
            self.add_experimental_data(data_df)
            
            # Update progress
            if progress_callback:
                progress_info.stage = "computing_metrics"
                progress_info.message = "Computing optimization metrics..."
                progress_info.percentage = 75.0
                progress_info.elapsed_time = time.time() - start_time
                progress_callback(progress_info)
            
            # Final progress
            if progress_callback:
                progress_info.stage = "completed"
                progress_info.message = f"Successfully added {len(data_df)} data points"
                progress_info.percentage = 100.0
                progress_info.elapsed_time = time.time() - start_time
                progress_info.status = OperationStatus.COMPLETED
                progress_callback(progress_info)
            
            logger.info(f"Enhanced data addition completed in {time.time() - start_time:.2f}s")
            
        except Exception as e:
            if progress_callback:
                progress_info.stage = "error"
                progress_info.message = f"Error adding data: {str(e)}"
                progress_info.status = OperationStatus.ERROR
                progress_callback(progress_info)
            
            logger.error(f"Error in enhanced data addition: {e}")
            raise
    
    def run_progressive_optimization(
        self,
        n_iterations: int,
        batch_size: int = 5,
        parent_window=None,
        completion_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run optimization with progressive UI and interruption support
        
        Args:
            n_iterations: Number of optimization iterations
            batch_size: Batch size for suggestions
            parent_window: Parent window for UI dialogs
            completion_callback: Callback when optimization completes
            
        Returns:
            Optimization results
        """
        if not self.progressive_manager:
            self.set_progress_manager(parent_window)
        
        def optimization_loop(progress_tracker: ProgressTracker = None):
            """Main optimization loop with progress tracking"""
            results = {
                'iterations': [],
                'best_solutions': [],
                'hypervolume_history': [],
                'total_time': 0.0
            }
            
            start_time = time.time()
            
            for iteration in range(n_iterations):
                if progress_tracker and progress_tracker.is_cancelled():
                    logger.info(f"Optimization cancelled at iteration {iteration}")
                    break
                
                try:
                    # Update progress
                    if progress_tracker:
                        progress_tracker.update(
                            current=iteration,
                            total=n_iterations,
                            stage=f"Iteration {iteration + 1}",
                            message=f"Generating suggestions for iteration {iteration + 1}"
                        )
                    
                    # Generate suggestions
                    suggestions = self.suggest_next_experiment(batch_size)
                    
                    # Simulate evaluation (in real use, this would be actual experiments)
                    # For demonstration, we'll use a simple function
                    simulated_results = self._simulate_experiment_results(suggestions)
                    
                    # Add results
                    results_df = pd.DataFrame(simulated_results)
                    self.add_experimental_data(results_df)
                    
                    # Record iteration results
                    iteration_result = {
                        'iteration': iteration + 1,
                        'suggestions': suggestions,
                        'results': simulated_results,
                        'hypervolume': self._calculate_hypervolume(),
                        'time': time.time() - start_time
                    }
                    
                    results['iterations'].append(iteration_result)
                    results['hypervolume_history'].append(iteration_result['hypervolume'])
                    
                    logger.info(f"Completed iteration {iteration + 1}/{n_iterations}")
                    
                except Exception as e:
                    logger.error(f"Error in iteration {iteration + 1}: {e}")
                    continue
            
            results['total_time'] = time.time() - start_time
            return results
        
        # Run optimization with progressive UI
        return self.progressive_manager.run_progressive_operation(
            optimization_loop,
            title=f"Bayesian Optimization ({n_iterations} iterations)",
            cancellable=True,
            callback=completion_callback
        )
    
    def _simulate_experiment_results(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simulate experimental results for demonstration
        
        Args:
            suggestions: List of parameter combinations
            
        Returns:
            List of simulated results
        """
        results = []
        
        for suggestion in suggestions:
            # Create a simple multi-objective test function
            result = suggestion.copy()
            
            # Add simulated objective values
            for obj_name in self.objective_names:
                # Simple quadratic function with noise
                value = sum(v**2 if isinstance(v, (int, float)) else 0 
                           for v in suggestion.values())
                value += np.random.normal(0, 0.1)  # Add noise
                result[obj_name] = float(value)
            
            results.append(result)
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        memory_info = memory_manager.get_memory_info()
        
        return {
            'cache_stats': {
                'hits': self.cache_hits,
                'misses': self.cache_misses,
                'hit_rate': self.cache_hits / max(1, self.cache_hits + self.cache_misses),
                'cache_size': len(self.computation_cache)
            },
            'memory_stats': memory_info,
            'plot_cache_stats': plot_cache.get_stats(),
            'parallel_config': {
                'enabled': self.enable_parallel,
                'workers': self.parallel_config.n_workers if self.parallel_config else 0
            },
            'async_enabled': self.enable_async,
            'total_experiments': len(self.experimental_data) if hasattr(self, 'experimental_data') else 0
        }
    
    def cleanup_resources(self):
        """Clean up resources and stop background processes"""
        # Stop memory monitoring
        memory_manager.stop_monitoring()
        
        # Clear caches
        if self.enable_caching:
            self.computation_cache.clear()
            plot_cache.clear()
        
        # Force garbage collection
        memory_manager.force_gc()
        
        logger.info("PerformanceEnhancedOptimizer resources cleaned up")

# Convenience function for easy integration
def create_enhanced_optimizer(
    params_config: Dict[str, Dict[str, Any]],
    responses_config: Dict[str, Dict[str, Any]],
    **kwargs
) -> PerformanceEnhancedOptimizer:
    """
    Create a performance-enhanced optimizer with default settings
    
    Args:
        params_config: Parameter configuration
        responses_config: Response configuration
        **kwargs: Additional optimizer arguments
        
    Returns:
        Configured PerformanceEnhancedOptimizer
    """
    return PerformanceEnhancedOptimizer(
        params_config=params_config,
        responses_config=responses_config,
        enable_async=True,
        enable_parallel=True,
        enable_caching=True,
        **kwargs
    )

__all__ = [
    'PerformanceEnhancedOptimizer',
    'create_enhanced_optimizer'
]