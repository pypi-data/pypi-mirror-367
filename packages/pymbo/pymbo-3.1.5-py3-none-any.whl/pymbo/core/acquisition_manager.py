"""
Acquisition Function Manager - Specialized Acquisition Function Management Module

This module provides a dedicated system for managing acquisition functions in 
multi-objective Bayesian optimization. It handles the setup, optimization, and
evaluation of various acquisition functions including Expected Improvement (EI),
Expected Hypervolume Improvement (EHVI), and Upper Confidence Bound (UCB).

Key Features:
- Efficient acquisition function setup and management
- Parallel acquisition function optimization
- Support for multiple acquisition strategies
- Adaptive acquisition function selection
- Thread-safe acquisition computations
- Memory-efficient optimization strategies

Classes:
    AcquisitionManager: Main acquisition function management engine
    AcquisitionOptimizer: Specialized optimizer for acquisition functions
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
from botorch.acquisition.analytic import LogExpectedImprovement, UpperConfidenceBound
from botorch.acquisition.multi_objective import ExpectedHypervolumeImprovement
from botorch.models import ModelListGP, SingleTaskGP
from botorch.optim import optimize_acqf
from botorch.utils.multi_objective.box_decompositions.non_dominated import (
    FastNondominatedPartitioning,
)
from scipy.optimize import minimize

logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_NUM_RESTARTS = 10
DEFAULT_RAW_SAMPLES = 100
MAX_OPTIMIZATION_TIME = 300  # 5 minutes timeout
DEFAULT_EXPLORATION_FACTOR = 2.0


class AcquisitionOptimizer:
    """
    Specialized optimizer for acquisition function optimization.
    """
    
    def __init__(
        self, 
        num_restarts: int = DEFAULT_NUM_RESTARTS,
        raw_samples: int = DEFAULT_RAW_SAMPLES,
        max_time: float = MAX_OPTIMIZATION_TIME
    ):
        """
        Initialize acquisition optimizer.
        
        Args:
            num_restarts: Number of optimization restarts
            raw_samples: Number of raw samples for initialization
            max_time: Maximum optimization time in seconds
        """
        self.num_restarts = num_restarts
        self.raw_samples = raw_samples
        self.max_time = max_time
        self._lock = threading.Lock()
        
    def optimize_acquisition(
        self,
        acq_function: Any,
        bounds: torch.Tensor,
        q: int = 1,
        device: torch.device = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Optimize acquisition function to find next candidate points.
        
        Args:
            acq_function: Acquisition function to optimize
            bounds: Optimization bounds tensor [2, n_dims]
            q: Number of candidates to generate
            device: PyTorch device
            
        Returns:
            Tuple of (candidates, acquisition_values)
        """
        try:
            with self._lock:
                start_time = time.time()
                
                # Use BoTorch's optimize_acqf for efficient optimization
                candidates, acq_values = optimize_acqf(
                    acq_function=acq_function,
                    bounds=bounds.to(device) if device else bounds,
                    q=q,
                    num_restarts=self.num_restarts,
                    raw_samples=self.raw_samples,
                    timeout=self.max_time
                )
                
                optimization_time = time.time() - start_time
                logger.debug(f"Acquisition optimization completed in {optimization_time:.3f}s")
                
                return candidates, acq_values
                
        except Exception as e:
            logger.error(f"Error optimizing acquisition function: {e}")
            # Return random candidates as fallback
            n_dims = bounds.shape[1]
            random_candidates = torch.rand(q, n_dims, device=device if device else torch.device("cpu"))
            return random_candidates, torch.zeros(q)


class AcquisitionManager:
    """
    Specialized manager for acquisition functions in Bayesian optimization.
    
    This class handles the setup, optimization, and evaluation of acquisition
    functions for both single and multi-objective optimization problems.
    """
    
    def __init__(
        self,
        device: torch.device = None,
        dtype: torch.dtype = torch.double,
        num_restarts: int = DEFAULT_NUM_RESTARTS,
        raw_samples: int = DEFAULT_RAW_SAMPLES,
        exploration_factor: float = DEFAULT_EXPLORATION_FACTOR
    ):
        """
        Initialize the acquisition manager.
        
        Args:
            device: PyTorch device for computations
            dtype: Data type for tensor operations
            num_restarts: Number of optimization restarts
            raw_samples: Number of raw samples for optimization
            exploration_factor: Exploration factor for acquisition functions
        """
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = dtype
        self.exploration_factor = exploration_factor
        
        # Initialize acquisition optimizer
        self.optimizer = AcquisitionOptimizer(num_restarts, raw_samples)
        
        # Storage for acquisition functions
        self._acquisition_functions = {}
        self._lock = threading.Lock()
        
        logger.info(f"AcquisitionManager initialized on {self.device}")
    
    def setup_single_objective_acquisition(
        self,
        model: SingleTaskGP,
        train_Y: torch.Tensor,
        acquisition_type: str = "EI"
    ) -> Optional[Any]:
        """
        Set up acquisition function for single-objective optimization.
        
        Args:
            model: Trained GP model
            train_Y: Training target values
            acquisition_type: Type of acquisition function ("EI", "UCB")
            
        Returns:
            Configured acquisition function or None if setup fails
        """
        try:
            # Filter finite values
            finite_Y = train_Y[torch.isfinite(train_Y)]
            if finite_Y.numel() == 0:
                logger.warning("No finite data points for acquisition setup")
                return None
            
            if acquisition_type.upper() == "EI":
                # Expected Improvement
                best_f = finite_Y.max()
                acq_func = LogExpectedImprovement(model=model, best_f=best_f)
                logger.debug(f"Set up Expected Improvement with best_f={best_f}")
                
            elif acquisition_type.upper() == "UCB":
                # Upper Confidence Bound
                acq_func = UpperConfidenceBound(model=model, beta=self.exploration_factor)
                logger.debug(f"Set up Upper Confidence Bound with beta={self.exploration_factor}")
                
            else:
                logger.error(f"Unknown acquisition type: {acquisition_type}")
                return None
            
            # Cache the acquisition function
            cache_key = f"single_{acquisition_type}_{id(model)}"
            with self._lock:
                self._acquisition_functions[cache_key] = acq_func
            
            return acq_func
            
        except Exception as e:
            logger.error(f"Error setting up single-objective acquisition: {e}")
            return None
    
    def setup_multi_objective_acquisition(
        self,
        model: Union[ModelListGP, SingleTaskGP],
        train_Y: torch.Tensor,
        ref_point: torch.Tensor = None,
        acquisition_type: str = "EHVI"
    ) -> Optional[Any]:
        """
        Set up acquisition function for multi-objective optimization.
        
        Args:
            model: Trained GP model(s)
            train_Y: Training target values
            ref_point: Reference point for hypervolume computation
            acquisition_type: Type of acquisition function ("EHVI")
            
        Returns:
            Configured acquisition function or None if setup fails
        """
        try:
            # Filter finite values
            finite_mask = torch.isfinite(train_Y).all(dim=1)
            if not finite_mask.any():
                logger.warning("No finite data points for multi-objective acquisition setup")
                return None
            
            clean_Y = train_Y[finite_mask]
            
            if acquisition_type.upper() == "EHVI":
                # Expected Hypervolume Improvement
                if ref_point is None:
                    # Calculate adaptive reference point
                    ref_point = self._calculate_adaptive_reference_point(clean_Y)
                
                logger.debug(f"Reference point for EHVI: {ref_point}")
                
                # Create partitioning
                partitioning = FastNondominatedPartitioning(
                    ref_point=ref_point, Y=clean_Y
                )
                
                acq_func = ExpectedHypervolumeImprovement(
                    model=model,
                    ref_point=ref_point.tolist(),
                    partitioning=partitioning,
                )
                
                logger.debug("Set up Expected Hypervolume Improvement")
                
            else:
                logger.error(f"Unknown multi-objective acquisition type: {acquisition_type}")
                return None
            
            # Cache the acquisition function
            cache_key = f"multi_{acquisition_type}_{id(model)}"
            with self._lock:
                self._acquisition_functions[cache_key] = acq_func
            
            return acq_func
            
        except Exception as e:
            logger.error(f"Error setting up multi-objective acquisition: {e}")
            return None
    
    def optimize_acquisition_function(
        self,
        acq_function: Any,
        bounds: torch.Tensor,
        n_candidates: int = 1
    ) -> List[torch.Tensor]:
        """
        Optimize acquisition function to find next candidate points.
        
        Args:
            acq_function: Acquisition function to optimize
            bounds: Parameter bounds tensor [2, n_dims]
            n_candidates: Number of candidates to generate
            
        Returns:
            List of candidate tensors
        """
        try:
            # Optimize acquisition function
            candidates, _ = self.optimizer.optimize_acquisition(
                acq_function=acq_function,
                bounds=bounds,
                q=n_candidates,
                device=self.device
            )
            
            # Convert to list of individual candidates
            candidate_list = []
            for i in range(candidates.shape[0]):
                candidate_list.append(candidates[i])
            
            logger.debug(f"Generated {len(candidate_list)} acquisition-optimized candidates")
            return candidate_list
            
        except Exception as e:
            logger.error(f"Error optimizing acquisition function: {e}")
            # Return random candidates as fallback
            n_dims = bounds.shape[1]
            random_candidates = []
            for _ in range(n_candidates):
                candidate = torch.rand(n_dims, device=self.device, dtype=self.dtype)
                random_candidates.append(candidate)
            return random_candidates
    
    def evaluate_acquisition_function(
        self,
        acq_function: Any,
        candidates: torch.Tensor
    ) -> torch.Tensor:
        """
        Evaluate acquisition function at given candidate points.
        
        Args:
            acq_function: Acquisition function to evaluate
            candidates: Candidate points tensor [n_candidates, n_dims]
            
        Returns:
            Acquisition values tensor [n_candidates]
        """
        try:
            with torch.no_grad():
                acq_values = acq_function(candidates.unsqueeze(-2))  # Add batch dimension
                return acq_values.squeeze()
                
        except Exception as e:
            logger.error(f"Error evaluating acquisition function: {e}")
            return torch.zeros(candidates.shape[0], device=self.device, dtype=self.dtype)
    
    def select_best_candidates(
        self,
        candidates: List[torch.Tensor],
        acq_function: Any,
        n_best: int = 1
    ) -> List[torch.Tensor]:
        """
        Select the best candidates based on acquisition function values.
        
        Args:
            candidates: List of candidate tensors
            acq_function: Acquisition function for evaluation
            n_best: Number of best candidates to select
            
        Returns:
            List of best candidate tensors
        """
        try:
            if not candidates:
                return []
            
            # Stack candidates for batch evaluation
            candidates_tensor = torch.stack(candidates)
            
            # Evaluate acquisition function
            acq_values = self.evaluate_acquisition_function(acq_function, candidates_tensor)
            
            # Select top candidates
            _, top_indices = torch.topk(acq_values, min(n_best, len(candidates)))
            
            best_candidates = [candidates[idx] for idx in top_indices]
            
            logger.debug(f"Selected {len(best_candidates)} best candidates from {len(candidates)}")
            return best_candidates
            
        except Exception as e:
            logger.error(f"Error selecting best candidates: {e}")
            return candidates[:n_best]  # Return first n_best as fallback
    
    def _calculate_adaptive_reference_point(self, clean_Y: torch.Tensor) -> torch.Tensor:
        """Calculate adaptive reference point for hypervolume computation."""
        try:
            min_observed_Y = clean_Y.min(dim=0)[0]
            max_observed_Y = clean_Y.max(dim=0)[0]
            
            # Calculate data range for each objective
            data_range = max_observed_Y - min_observed_Y
            
            # Use adaptive offset
            adaptive_offset = torch.maximum(
                data_range * 0.1, torch.ones_like(data_range) * 0.1
            )
            
            adaptive_offset = torch.maximum(
                adaptive_offset, torch.ones_like(data_range) * 0.01
            )
            
            ref_point = min_observed_Y - adaptive_offset
            ref_point = torch.nan_to_num(ref_point, nan=-1.0)
            
            return ref_point
            
        except Exception as e:
            logger.error(f"Error calculating adaptive reference point: {e}")
            return torch.full((clean_Y.shape[1],), -1.0, device=self.device, dtype=self.dtype)
    
    def get_acquisition_function(self, cache_key: str) -> Optional[Any]:
        """Retrieve cached acquisition function."""
        with self._lock:
            return self._acquisition_functions.get(cache_key)
    
    def clear_cache(self) -> None:
        """Clear all cached acquisition functions."""
        with self._lock:
            self._acquisition_functions.clear()
        logger.debug("Acquisition function cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get acquisition function cache statistics."""
        with self._lock:
            return {
                "cached_functions": len(self._acquisition_functions),
                "single_objective": sum(1 for k in self._acquisition_functions.keys() if k.startswith("single")),
                "multi_objective": sum(1 for k in self._acquisition_functions.keys() if k.startswith("multi"))
            }
    
    def setup_acquisition_function(
        self,
        model: Union[SingleTaskGP, ModelListGP],
        train_Y: torch.Tensor,
        objective_names: List[str],
        ref_point: torch.Tensor = None
    ) -> Optional[Any]:
        """
        Automatically setup appropriate acquisition function based on problem type.
        
        Args:
            model: Trained GP model(s)
            train_Y: Training target values
            objective_names: List of objective names
            ref_point: Optional reference point for multi-objective
            
        Returns:
            Configured acquisition function or None if setup fails
        """
        try:
            if len(objective_names) == 1:
                # Single objective optimization
                return self.setup_single_objective_acquisition(model, train_Y, "EI")
            else:
                # Multi-objective optimization
                return self.setup_multi_objective_acquisition(model, train_Y, ref_point, "EHVI")
                
        except Exception as e:
            logger.error(f"Error in automatic acquisition setup: {e}")
            return None