"""
Gradient Calculator - Specialized Gradient Computation Module for SGLBO

This module provides efficient gradient calculation capabilities for the 
Stochastic Gradient Line Bayesian Optimization (SGLBO) screening method.
It handles numerical gradient computation, gradient composition, and 
optimization direction management.

Key Features:
- High-performance numerical gradient computation
- Multi-objective gradient composition
- Adaptive step size management
- Thread-safe gradient operations
- Memory-efficient gradient caching

Classes:
    GradientCalculator: Main gradient computation engine
"""

import logging
import threading
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor

logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_GRADIENT_STEP = 1e-6
MIN_GRADIENT_NORM = 1e-8
MAX_GRADIENT_NORM = 10.0


class GradientCalculator:
    """
    Specialized gradient calculator for SGLBO optimization.
    
    This class provides efficient gradient computation for Gaussian Process
    models in the context of screening optimization.
    """
    
    def __init__(
        self,
        gradient_step: float = DEFAULT_GRADIENT_STEP,
        enable_caching: bool = True
    ):
        """
        Initialize gradient calculator.
        
        Args:
            gradient_step: Step size for numerical gradient computation
            enable_caching: Whether to enable gradient caching
        """
        self.gradient_step = gradient_step
        self.enable_caching = enable_caching
        
        # Gradient cache
        self._gradient_cache = {} if enable_caching else None
        self._lock = threading.Lock()
        
        logger.info(f"GradientCalculator initialized with step size {gradient_step}")
    
    def calculate_numerical_gradient(
        self,
        gp_model: GaussianProcessRegressor,
        params_normalized: np.ndarray,
        objective_direction: int = 1
    ) -> np.ndarray:
        """
        Calculate numerical gradient of GP model at given parameters.
        
        Args:
            gp_model: Trained Gaussian Process model
            params_normalized: Parameter values in normalized space
            objective_direction: 1 for maximize, -1 for minimize, 0 for target
            
        Returns:
            Gradient vector
        """
        try:
            # Check cache first
            cache_key = None
            if self.enable_caching:
                cache_key = self._generate_cache_key(params_normalized, id(gp_model))
                with self._lock:
                    if cache_key in self._gradient_cache:
                        cached_gradient = self._gradient_cache[cache_key]
                        return cached_gradient * objective_direction
            
            gradient = np.zeros_like(params_normalized)
            h = self.gradient_step
            
            # Calculate numerical gradient using central difference
            for i in range(len(params_normalized)):
                params_plus = params_normalized.copy()
                params_minus = params_normalized.copy()
                
                # Ensure we stay within bounds [0, 1]
                params_plus[i] = min(1.0, params_plus[i] + h)
                params_minus[i] = max(0.0, params_minus[i] - h)
                
                # Predict at both points
                pred_plus, _ = gp_model.predict([params_plus], return_std=True)
                pred_minus, _ = gp_model.predict([params_minus], return_std=True)
                
                # Calculate gradient component
                delta_x = params_plus[i] - params_minus[i]
                if delta_x > 1e-12:
                    gradient[i] = (pred_plus[0] - pred_minus[0]) / delta_x
                else:
                    gradient[i] = 0.0
            
            # Normalize gradient to prevent numerical issues
            gradient_norm = np.linalg.norm(gradient)
            if gradient_norm > MAX_GRADIENT_NORM:
                gradient = gradient * (MAX_GRADIENT_NORM / gradient_norm)
            elif gradient_norm < MIN_GRADIENT_NORM and gradient_norm > 0:
                gradient = gradient * (MIN_GRADIENT_NORM / gradient_norm)
            
            # Cache the raw gradient
            if self.enable_caching and cache_key:
                with self._lock:
                    self._gradient_cache[cache_key] = gradient.copy()
            
            # Apply objective direction
            return gradient * objective_direction
            
        except Exception as e:
            logger.error(f"Error calculating numerical gradient: {e}")
            return np.zeros_like(params_normalized)
    
    def calculate_target_gradient(
        self,
        gp_model: GaussianProcessRegressor,
        params_normalized: np.ndarray,
        target_value: float
    ) -> np.ndarray:
        """
        Calculate gradient for target-seeking objective.
        
        Args:
            gp_model: Trained Gaussian Process model
            params_normalized: Parameter values in normalized space
            target_value: Target value to seek
            
        Returns:
            Gradient vector pointing toward target
        """
        try:
            # Get current prediction
            current_pred, _ = gp_model.predict([params_normalized], return_std=True)
            current_value = current_pred[0]
            
            # Calculate raw gradient
            raw_gradient = self.calculate_numerical_gradient(gp_model, params_normalized, 1)
            
            # Determine direction to target
            if current_value > target_value:
                # We're above target, need to decrease
                return -raw_gradient
            elif current_value < target_value:
                # We're below target, need to increase
                return raw_gradient
            else:
                # We're at target, no gradient
                return np.zeros_like(params_normalized)
                
        except Exception as e:
            logger.error(f"Error calculating target gradient: {e}")
            return np.zeros_like(params_normalized)
    
    def compose_multi_objective_gradient(
        self,
        gradients: List[np.ndarray],
        weights: Optional[List[float]] = None
    ) -> np.ndarray:
        """
        Compose multiple objective gradients into a single gradient.
        
        Args:
            gradients: List of gradient vectors
            weights: Optional weights for each objective
            
        Returns:
            Composed gradient vector
        """
        try:
            if not gradients:
                logger.warning("No gradients provided for composition")
                return np.zeros(0)
            
            if len(gradients) == 1:
                return gradients[0]
            
            # Use equal weights if not provided
            if weights is None:
                weights = [1.0 / len(gradients)] * len(gradients)
            
            if len(weights) != len(gradients):
                logger.warning("Mismatch between gradients and weights, using equal weights")
                weights = [1.0 / len(gradients)] * len(gradients)
            
            # Compose weighted gradient
            composite_gradient = np.zeros_like(gradients[0])
            
            for gradient, weight in zip(gradients, weights):
                # Normalize individual gradient
                gradient_norm = np.linalg.norm(gradient)
                if gradient_norm > MIN_GRADIENT_NORM:
                    normalized_gradient = gradient / gradient_norm
                    composite_gradient += weight * normalized_gradient
            
            # Normalize final composite gradient
            composite_norm = np.linalg.norm(composite_gradient)
            if composite_norm > MIN_GRADIENT_NORM:
                composite_gradient = composite_gradient / composite_norm
            
            return composite_gradient
            
        except Exception as e:
            logger.error(f"Error composing multi-objective gradient: {e}")
            return np.zeros_like(gradients[0]) if gradients else np.zeros(0)
    
    def calculate_adaptive_step_size(
        self,
        gradient: np.ndarray,
        current_params: np.ndarray,
        base_step_size: float = 0.1,
        max_step_size: float = 0.5,
        min_step_size: float = 0.01
    ) -> float:
        """
        Calculate adaptive step size based on gradient magnitude and parameter bounds.
        
        Args:
            gradient: Current gradient vector
            current_params: Current parameter values
            base_step_size: Base step size
            max_step_size: Maximum allowed step size
            min_step_size: Minimum allowed step size
            
        Returns:
            Adapted step size
        """
        try:
            gradient_norm = np.linalg.norm(gradient)
            
            if gradient_norm < MIN_GRADIENT_NORM:
                return min_step_size
            
            # Calculate how far we can move in each direction
            max_forward_step = np.inf
            max_backward_step = np.inf
            
            for i, (param, grad_component) in enumerate(zip(current_params, gradient)):
                if abs(grad_component) > 1e-12:
                    if grad_component > 0:
                        # Moving toward 1.0
                        max_forward_step = min(max_forward_step, (1.0 - param) / grad_component)
                    else:
                        # Moving toward 0.0
                        max_backward_step = min(max_backward_step, param / abs(grad_component))
            
            # Use the smaller of the two limits
            max_feasible_step = min(max_forward_step, max_backward_step)
            
            # Adaptive step size based on gradient norm
            if gradient_norm > 1.0:
                adapted_step = base_step_size / gradient_norm
            else:
                adapted_step = base_step_size * gradient_norm
            
            # Apply bounds and feasibility constraints
            adapted_step = min(adapted_step, max_feasible_step * 0.8)  # Leave some margin
            adapted_step = max(min_step_size, min(adapted_step, max_step_size))
            
            return adapted_step
            
        except Exception as e:
            logger.error(f"Error calculating adaptive step size: {e}")
            return base_step_size
    
    def validate_gradient_step(
        self,
        current_params: np.ndarray,
        gradient: np.ndarray,
        step_size: float
    ) -> Tuple[np.ndarray, float]:
        """
        Validate and adjust gradient step to ensure parameters stay within bounds.
        
        Args:
            current_params: Current parameter values
            gradient: Gradient vector
            step_size: Proposed step size
            
        Returns:
            Tuple of (adjusted_gradient, adjusted_step_size)
        """
        try:
            proposed_params = current_params + step_size * gradient
            
            # Check bounds and adjust if necessary
            adjusted_gradient = gradient.copy()
            adjusted_step_size = step_size
            
            # Find the maximum feasible step size
            max_feasible_step = step_size
            
            for i, (current, proposed, grad_comp) in enumerate(zip(current_params, proposed_params, gradient)):
                if proposed < 0.0:
                    if abs(grad_comp) > 1e-12:
                        max_feasible_step = min(max_feasible_step, -current / grad_comp)
                elif proposed > 1.0:
                    if abs(grad_comp) > 1e-12:
                        max_feasible_step = min(max_feasible_step, (1.0 - current) / grad_comp)
            
            if max_feasible_step < step_size:
                adjusted_step_size = max_feasible_step * 0.95  # Leave small margin
                logger.debug(f"Adjusted step size from {step_size:.4f} to {adjusted_step_size:.4f}")
            
            return adjusted_gradient, adjusted_step_size
            
        except Exception as e:
            logger.error(f"Error validating gradient step: {e}")
            return gradient, step_size
    
    def _generate_cache_key(self, params: np.ndarray, model_id: int) -> str:
        """Generate cache key for gradient storage."""
        try:
            params_hash = hash(params.tobytes())
            return f"grad_{model_id}_{params_hash}"
        except Exception:
            return f"grad_{model_id}_{np.random.randint(0, 1000000)}"
    
    def clear_cache(self) -> None:
        """Clear gradient cache."""
        if self.enable_caching:
            with self._lock:
                if self._gradient_cache:
                    self._gradient_cache.clear()
            logger.debug("Gradient cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get gradient cache statistics."""
        if self.enable_caching and self._gradient_cache:
            with self._lock:
                return {"cached_gradients": len(self._gradient_cache)}
        return {"cached_gradients": 0}
    
    def set_gradient_step(self, new_step: float) -> None:
        """Update gradient step size."""
        if new_step > 0:
            self.gradient_step = new_step
            self.clear_cache()  # Clear cache since step size affects gradients
            logger.info(f"Gradient step size updated to {new_step}")
        else:
            logger.warning("Invalid gradient step size, keeping current value")