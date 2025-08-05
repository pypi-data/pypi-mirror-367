"""
Acquisition Evaluator - Specialized Acquisition Function Evaluation for SGLBO

This module provides efficient acquisition function evaluation capabilities
for the Stochastic Gradient Line Bayesian Optimization (SGLBO) screening method.
It handles Upper Confidence Bound (UCB) evaluation, multi-objective acquisition
composition, and acquisition-based candidate selection.

Key Features:
- High-performance UCB acquisition evaluation
- Multi-objective acquisition function composition
- Exploration-exploitation balance management
- Thread-safe acquisition operations
- Memory-efficient evaluation caching

Classes:
    AcquisitionEvaluator: Main acquisition evaluation engine
"""

import logging
import threading
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor

logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_EXPLORATION_FACTOR = 0.1
MIN_ACQUISITION_VALUE = -1e6
MAX_ACQUISITION_VALUE = 1e6


class AcquisitionEvaluator:
    """
    Specialized acquisition function evaluator for SGLBO screening.
    
    This class provides efficient acquisition function evaluation for
    screening optimization using Upper Confidence Bound and related methods.
    """
    
    def __init__(
        self,
        exploration_factor: float = DEFAULT_EXPLORATION_FACTOR,
        enable_caching: bool = True
    ):
        """
        Initialize acquisition evaluator.
        
        Args:
            exploration_factor: Balance between exploration and exploitation
            enable_caching: Whether to enable acquisition value caching
        """
        self.exploration_factor = exploration_factor
        self.enable_caching = enable_caching
        
        # Acquisition cache
        self._acquisition_cache = {} if enable_caching else None
        self._lock = threading.Lock()
        
        logger.info(f"AcquisitionEvaluator initialized with exploration factor {exploration_factor}")
    
    def evaluate_ucb_acquisition(
        self,
        gp_model: GaussianProcessRegressor,
        params_normalized: np.ndarray,
        objective_direction: int = 1
    ) -> float:
        """
        Evaluate Upper Confidence Bound acquisition function.
        
        Args:
            gp_model: Trained Gaussian Process model
            params_normalized: Parameter values in normalized space
            objective_direction: 1 for maximize, -1 for minimize
            
        Returns:
            UCB acquisition value
        """
        try:
            # Check cache first
            cache_key = None
            if self.enable_caching:
                cache_key = self._generate_cache_key(params_normalized, id(gp_model), "ucb")
                with self._lock:
                    if cache_key in self._acquisition_cache:
                        cached_value = self._acquisition_cache[cache_key]
                        return cached_value * objective_direction
            
            # Predict mean and standard deviation
            mean, std = gp_model.predict([params_normalized], return_std=True)
            mean_val = mean[0]
            std_val = max(std[0], 1e-6)  # Avoid division by zero
            
            # Calculate UCB
            ucb_value = mean_val + self.exploration_factor * std_val
            
            # Apply bounds to prevent numerical issues
            ucb_value = max(MIN_ACQUISITION_VALUE, min(ucb_value, MAX_ACQUISITION_VALUE))
            
            # Cache the raw value
            if self.enable_caching and cache_key:
                with self._lock:
                    self._acquisition_cache[cache_key] = ucb_value
            
            # Apply objective direction
            return ucb_value * objective_direction
            
        except Exception as e:
            logger.error(f"Error evaluating UCB acquisition: {e}")
            return 0.0
    
    def evaluate_target_acquisition(
        self,
        gp_model: GaussianProcessRegressor,
        params_normalized: np.ndarray,
        target_value: float
    ) -> float:
        """
        Evaluate acquisition function for target-seeking objective.
        
        Args:
            gp_model: Trained Gaussian Process model
            params_normalized: Parameter values in normalized space
            target_value: Target value to seek
            
        Returns:
            Target-based acquisition value
        """
        try:
            # Check cache first
            cache_key = None
            if self.enable_caching:
                cache_key = self._generate_cache_key(params_normalized, id(gp_model), f"target_{target_value}")
                with self._lock:
                    if cache_key in self._acquisition_cache:
                        return self._acquisition_cache[cache_key]
            
            # Predict mean and standard deviation
            mean, std = gp_model.predict([params_normalized], return_std=True)
            mean_val = mean[0]
            std_val = max(std[0], 1e-6)
            
            # Calculate target-based acquisition
            # Negative absolute deviation from target, plus exploration term
            deviation = abs(mean_val - target_value)
            acquisition_value = -deviation + self.exploration_factor * std_val
            
            # Apply bounds
            acquisition_value = max(MIN_ACQUISITION_VALUE, min(acquisition_value, MAX_ACQUISITION_VALUE))
            
            # Cache the value
            if self.enable_caching and cache_key:
                with self._lock:
                    self._acquisition_cache[cache_key] = acquisition_value
            
            return acquisition_value
            
        except Exception as e:
            logger.error(f"Error evaluating target acquisition: {e}")
            return 0.0
    
    def evaluate_multi_objective_acquisition(
        self,
        gp_models: Dict[str, GaussianProcessRegressor],
        params_normalized: np.ndarray,
        objective_directions: Dict[str, int],
        target_values: Dict[str, float] = None,
        weights: Dict[str, float] = None
    ) -> float:
        """
        Evaluate acquisition function for multiple objectives.
        
        Args:
            gp_models: Dictionary of trained GP models for each objective
            params_normalized: Parameter values in normalized space
            objective_directions: Direction for each objective (1=max, -1=min, 0=target)
            target_values: Target values for objectives with direction 0
            weights: Weights for each objective (default: equal weights)
            
        Returns:
            Composed multi-objective acquisition value
        """
        try:
            if not gp_models:
                return 0.0
            
            objective_names = list(gp_models.keys())
            
            # Use equal weights if not provided
            if weights is None:
                weights = {name: 1.0 / len(objective_names) for name in objective_names}
            
            # Normalize weights
            total_weight = sum(weights.values())
            if total_weight > 0:
                weights = {name: w / total_weight for name, w in weights.items()}
            else:
                weights = {name: 1.0 / len(objective_names) for name in objective_names}
            
            total_acquisition = 0.0
            
            for obj_name in objective_names:
                if obj_name not in gp_models:
                    continue
                
                gp_model = gp_models[obj_name]
                direction = objective_directions.get(obj_name, 1)
                weight = weights.get(obj_name, 0.0)
                
                if direction == 0:  # Target objective
                    target_val = target_values.get(obj_name, 0.0) if target_values else 0.0
                    acquisition_val = self.evaluate_target_acquisition(gp_model, params_normalized, target_val)
                else:  # Maximize or minimize objective
                    acquisition_val = self.evaluate_ucb_acquisition(gp_model, params_normalized, direction)
                
                total_acquisition += weight * acquisition_val
            
            return total_acquisition
            
        except Exception as e:
            logger.error(f"Error evaluating multi-objective acquisition: {e}")
            return 0.0
    
    def compare_candidates(
        self,
        candidates: List[np.ndarray],
        gp_models: Dict[str, GaussianProcessRegressor],
        objective_directions: Dict[str, int],
        target_values: Dict[str, float] = None,
        weights: Dict[str, float] = None
    ) -> Tuple[np.ndarray, float]:
        """
        Compare multiple candidates and return the best one based on acquisition function.
        
        Args:
            candidates: List of candidate parameter arrays
            gp_models: Dictionary of trained GP models
            objective_directions: Direction for each objective
            target_values: Target values for objectives with direction 0
            weights: Weights for each objective
            
        Returns:
            Tuple of (best_candidate, best_acquisition_value)
        """
        try:
            if not candidates:
                logger.warning("No candidates provided for comparison")
                return np.array([]), 0.0
            
            if len(candidates) == 1:
                acquisition_val = self.evaluate_multi_objective_acquisition(
                    gp_models, candidates[0], objective_directions, target_values, weights
                )
                return candidates[0], acquisition_val
            
            best_candidate = candidates[0]
            best_acquisition = self.evaluate_multi_objective_acquisition(
                gp_models, candidates[0], objective_directions, target_values, weights
            )
            
            for candidate in candidates[1:]:
                acquisition_val = self.evaluate_multi_objective_acquisition(
                    gp_models, candidate, objective_directions, target_values, weights
                )
                
                if acquisition_val > best_acquisition:
                    best_candidate = candidate
                    best_acquisition = acquisition_val
            
            logger.debug(f"Best candidate selected with acquisition value: {best_acquisition:.4f}")
            return best_candidate, best_acquisition
            
        except Exception as e:
            logger.error(f"Error comparing candidates: {e}")
            return candidates[0] if candidates else np.array([]), 0.0
    
    def evaluate_batch_acquisition(
        self,
        candidates: List[np.ndarray],
        gp_models: Dict[str, GaussianProcessRegressor],
        objective_directions: Dict[str, int],
        target_values: Dict[str, float] = None,
        weights: Dict[str, float] = None
    ) -> List[float]:
        """
        Evaluate acquisition function for a batch of candidates.
        
        Args:
            candidates: List of candidate parameter arrays
            gp_models: Dictionary of trained GP models
            objective_directions: Direction for each objective
            target_values: Target values for objectives with direction 0
            weights: Weights for each objective
            
        Returns:
            List of acquisition values for each candidate
        """
        try:
            acquisition_values = []
            
            for candidate in candidates:
                acquisition_val = self.evaluate_multi_objective_acquisition(
                    gp_models, candidate, objective_directions, target_values, weights
                )
                acquisition_values.append(acquisition_val)
            
            return acquisition_values
            
        except Exception as e:
            logger.error(f"Error evaluating batch acquisition: {e}")
            return [0.0] * len(candidates)
    
    def get_exploration_exploitation_balance(
        self,
        gp_model: GaussianProcessRegressor,
        params_normalized: np.ndarray
    ) -> Dict[str, float]:
        """
        Get the exploration and exploitation components of the acquisition function.
        
        Args:
            gp_model: Trained Gaussian Process model
            params_normalized: Parameter values in normalized space
            
        Returns:
            Dictionary with exploration and exploitation values
        """
        try:
            # Predict mean and standard deviation
            mean, std = gp_model.predict([params_normalized], return_std=True)
            mean_val = mean[0]
            std_val = max(std[0], 1e-6)
            
            exploitation = mean_val
            exploration = self.exploration_factor * std_val
            
            return {
                "exploitation": exploitation,
                "exploration": exploration,
                "total_ucb": exploitation + exploration,
                "exploration_ratio": exploration / (abs(exploitation) + exploration + 1e-6)
            }
            
        except Exception as e:
            logger.error(f"Error getting exploration-exploitation balance: {e}")
            return {"exploitation": 0.0, "exploration": 0.0, "total_ucb": 0.0, "exploration_ratio": 0.5}
    
    def _generate_cache_key(self, params: np.ndarray, model_id: int, acquisition_type: str) -> str:
        """Generate cache key for acquisition value storage."""
        try:
            params_hash = hash(params.tobytes())
            return f"acq_{acquisition_type}_{model_id}_{params_hash}_{self.exploration_factor}"
        except Exception:
            return f"acq_{acquisition_type}_{model_id}_{np.random.randint(0, 1000000)}"
    
    def clear_cache(self) -> None:
        """Clear acquisition cache."""
        if self.enable_caching:
            with self._lock:
                if self._acquisition_cache:
                    self._acquisition_cache.clear()
            logger.debug("Acquisition cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get acquisition cache statistics."""
        if self.enable_caching and self._acquisition_cache:
            with self._lock:
                return {"cached_acquisitions": len(self._acquisition_cache)}
        return {"cached_acquisitions": 0}
    
    def set_exploration_factor(self, new_factor: float) -> None:
        """Update exploration factor."""
        if new_factor >= 0:
            self.exploration_factor = new_factor
            self.clear_cache()  # Clear cache since exploration factor affects values
            logger.info(f"Exploration factor updated to {new_factor}")
        else:
            logger.warning("Invalid exploration factor, keeping current value")