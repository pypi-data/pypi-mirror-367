"""
Optimization Controller - Specialized Controller for Optimization Operations

This module provides a dedicated controller for optimization-specific operations,
extracted from the main controller for better performance and modularity.
It handles experiment suggestion, data submission, and optimization flow management.

Key Features:
- High-performance experiment suggestion generation
- Efficient data submission and model updates
- Optimization flow management
- Thread-safe optimization operations
- Memory-efficient suggestion caching

Classes:
    OptimizationController: Main optimization operations controller
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class OptimizationController:
    """
    Specialized controller for optimization operations in Bayesian optimization.
    
    This controller handles all aspects of the optimization process including
    experiment suggestion, data management, and optimization flow control.
    """
    
    def __init__(self, optimizer: Any = None):
        """
        Initialize optimization controller.
        
        Args:
            optimizer: The optimization engine instance
        """
        self.optimizer = optimizer
        self._suggestion_cache = {}
        self._last_suggestion_time = 0
        self._lock = threading.Lock()
        
        logger.info("OptimizationController initialized")
    
    def set_optimizer(self, optimizer: Any) -> None:
        """Set the optimization engine."""
        with self._lock:
            self.optimizer = optimizer
        logger.info("Optimizer set in OptimizationController")
    
    def generate_initial_suggestion(self) -> Dict[str, Any]:
        """
        Generate the first experiment suggestion for a new optimization.
        
        Returns:
            Dictionary with initial parameter suggestion
        """
        try:
            if not self.optimizer:
                logger.warning("No optimizer available for initial suggestion")
                return {}
            
            logger.info("Generating initial suggestion...")
            suggestions = self.optimizer.suggest_next_experiment(n_suggestions=1)
            
            if suggestions:
                suggestion = suggestions[0]
                logger.info(f"Initial suggestion generated: {suggestion}")
                
                # Cache the suggestion
                self._cache_suggestion("initial", suggestion)
                return suggestion
            else:
                logger.warning("No initial suggestion generated")
                return {}
                
        except Exception as e:
            logger.error(f"Error generating initial suggestion: {e}", exc_info=True)
            return {}
    
    def generate_batch_suggestions(
        self, 
        num_suggestions: int,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate a batch of experiment suggestions.
        
        Args:
            num_suggestions: Number of suggestions to generate
            use_cache: Whether to use cached results if available
            
        Returns:
            List of parameter suggestion dictionaries
        """
        try:
            if not self.optimizer:
                logger.warning("No optimizer available for batch suggestions")
                return []
            
            # Check cache first
            cache_key = f"batch_{num_suggestions}"
            if use_cache:
                cached_suggestions = self._get_cached_suggestions(cache_key)
                if cached_suggestions:
                    logger.debug(f"Using cached batch suggestions: {len(cached_suggestions)}")
                    return cached_suggestions
            
            logger.info(f"Generating {num_suggestions} batch suggestions...")
            
            # Generate suggestions using the optimizer
            suggestions = self.optimizer.suggest_next_experiment(n_suggestions=num_suggestions)
            
            if suggestions:
                logger.info(f"Generated {len(suggestions)} suggestions")
                
                # Cache the suggestions
                self._cache_suggestion(cache_key, suggestions)
                return suggestions
            else:
                logger.warning("No batch suggestions generated")
                return []
                
        except Exception as e:
            logger.error(f"Error generating batch suggestions: {e}", exc_info=True)
            return []
    
    def submit_experiment_result(
        self,
        parameters: Dict[str, Any],
        responses: Dict[str, float],
        validate_data: bool = True
    ) -> bool:
        """
        Submit experimental results to the optimizer.
        
        Args:
            parameters: Dictionary of parameter values
            responses: Dictionary of response values
            validate_data: Whether to validate input data
            
        Returns:
            True if submission successful, False otherwise
        """
        try:
            if not self.optimizer:
                logger.error("No optimizer available for result submission")
                return False
            
            logger.info(f"Submitting experiment result: {responses}")
            
            # Input validation
            if validate_data:
                if not self._validate_experiment_data(parameters, responses):
                    return False
            
            # Combine parameters and responses
            data_record = {**parameters, **responses}
            data_df = pd.DataFrame([data_record])
            
            # Submit to optimizer
            self.optimizer.add_experimental_data(data_df)
            
            # Clear suggestion cache since model has been updated
            self._clear_suggestion_cache()
            
            logger.info(f"Experiment result submitted successfully. Total experiments: {len(self.optimizer.experimental_data)}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting experiment result: {e}", exc_info=True)
            return False
    
    def submit_batch_results(
        self,
        batch_data: List[Dict[str, Any]],
        validate_data: bool = True
    ) -> bool:
        """
        Submit batch experimental results to the optimizer.
        
        Args:
            batch_data: List of experiment records (parameters + responses)
            validate_data: Whether to validate input data
            
        Returns:
            True if submission successful, False otherwise
        """
        try:
            if not self.optimizer:
                logger.error("No optimizer available for batch result submission")
                return False
            
            if not batch_data:
                logger.warning("No batch data provided")
                return False
            
            logger.info(f"Submitting batch results: {len(batch_data)} experiments")
            
            # Validate data if requested
            if validate_data:
                valid_data = []
                for i, record in enumerate(batch_data):
                    # Split into parameters and responses
                    param_names = list(self.optimizer.params_config.keys()) if hasattr(self.optimizer, 'params_config') else []
                    response_names = list(self.optimizer.responses_config.keys()) if hasattr(self.optimizer, 'responses_config') else []
                    
                    parameters = {k: v for k, v in record.items() if k in param_names}
                    responses = {k: v for k, v in record.items() if k in response_names}
                    
                    if self._validate_experiment_data(parameters, responses):
                        valid_data.append(record)
                    else:
                        logger.warning(f"Skipping invalid data record {i}")
                
                if not valid_data:
                    logger.error("No valid data records in batch")
                    return False
                
                batch_data = valid_data
            
            # Convert to DataFrame and submit
            data_df = pd.DataFrame(batch_data)
            self.optimizer.add_experimental_data(data_df)
            
            # Clear suggestion cache
            self._clear_suggestion_cache()
            
            logger.info(f"Batch results submitted successfully. Total experiments: {len(self.optimizer.experimental_data)}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting batch results: {e}", exc_info=True)
            return False
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """
        Get current optimization status and statistics.
        
        Returns:
            Dictionary with optimization status information
        """
        try:
            if not self.optimizer:
                return {"status": "no_optimizer", "message": "No optimizer initialized"}
            
            status = {
                "status": "active",
                "total_experiments": len(getattr(self.optimizer, 'experimental_data', pd.DataFrame())),
                "has_data": hasattr(self.optimizer, 'experimental_data') and not self.optimizer.experimental_data.empty,
                "objectives": getattr(self.optimizer, 'objective_names', []),
                "parameters": list(getattr(self.optimizer, 'params_config', {}).keys()),
            }
            
            # Add hypervolume information if available
            try:
                if hasattr(self.optimizer, '_calculate_hypervolume'):
                    hv_data = self.optimizer._calculate_hypervolume()
                    status["hypervolume"] = hv_data
            except Exception as e:
                logger.debug(f"Could not get hypervolume data: {e}")
            
            # Add convergence information if available
            try:
                if hasattr(self.optimizer, 'check_hypervolume_convergence'):
                    convergence_data = self.optimizer.check_hypervolume_convergence()
                    status["convergence"] = convergence_data
            except Exception as e:
                logger.debug(f"Could not get convergence data: {e}")
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting optimization status: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_pareto_front(self) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
        """
        Get Pareto front data from the optimizer.
        
        Returns:
            Tuple of (pareto_parameters, pareto_objectives, pareto_indices)
        """
        try:
            if not self.optimizer or not hasattr(self.optimizer, 'get_pareto_front'):
                logger.warning("Optimizer not available or doesn't support Pareto front")
                return pd.DataFrame(), pd.DataFrame(), np.array([])
            
            return self.optimizer.get_pareto_front()
            
        except Exception as e:
            logger.error(f"Error getting Pareto front: {e}")
            return pd.DataFrame(), pd.DataFrame(), np.array([])
    
    def get_best_solution(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Get the best compromise solution from the optimizer.
        
        Returns:
            Tuple of (best_parameters, best_responses)
        """
        try:
            if not self.optimizer or not hasattr(self.optimizer, 'get_best_compromise_solution'):
                logger.warning("Optimizer not available or doesn't support best solution")
                return {}, {}
            
            return self.optimizer.get_best_compromise_solution()
            
        except Exception as e:
            logger.error(f"Error getting best solution: {e}")
            return {}, {}
    
    def predict_responses(self, parameters: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """
        Predict responses for given parameters using the trained models.
        
        Args:
            parameters: Parameter values for prediction
            
        Returns:
            Dictionary with predicted responses (mean, CI, etc.)
        """
        try:
            if not self.optimizer or not hasattr(self.optimizer, 'predict_responses_at'):
                logger.warning("Optimizer not available or doesn't support prediction")
                return {}
            
            return self.optimizer.predict_responses_at(parameters)
            
        except Exception as e:
            logger.error(f"Error predicting responses: {e}")
            return {}
    
    def _validate_experiment_data(
        self, 
        parameters: Dict[str, Any], 
        responses: Dict[str, float]
    ) -> bool:
        """
        Validate experimental data before submission.
        
        Args:
            parameters: Parameter values
            responses: Response values
            
        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Check for empty data
            if not parameters or not responses:
                logger.error("Parameters or responses are empty")
                return False
            
            # Check for parameter/response name conflicts
            param_names = set(parameters.keys())
            response_names = set(responses.keys())
            conflicts = param_names & response_names
            if conflicts:
                logger.error(f"Parameter and response names conflict: {conflicts}")
                return False
            
            # Validate parameter values
            for param_name, value in parameters.items():
                if not isinstance(value, (int, float, str)):
                    logger.error(f"Invalid parameter value type for '{param_name}': {type(value)}")
                    return False
            
            # Validate response values
            for response_name, value in responses.items():
                if not isinstance(value, (int, float)):
                    logger.error(f"Response '{response_name}' must be numeric, got {type(value)}")
                    return False
                if not np.isfinite(value):
                    logger.error(f"Response '{response_name}' must be finite, got {value}")
                    return False
            
            # Validate against optimizer configuration if available
            if self.optimizer:
                if hasattr(self.optimizer, 'params_config'):
                    expected_params = set(self.optimizer.params_config.keys())
                    provided_params = set(parameters.keys())
                    missing_params = expected_params - provided_params
                    if missing_params:
                        logger.error(f"Missing required parameters: {missing_params}")
                        return False
                
                if hasattr(self.optimizer, 'responses_config'):
                    expected_responses = set(self.optimizer.responses_config.keys())
                    provided_responses = set(responses.keys())
                    # At least one response should be provided
                    if not (provided_responses & expected_responses):
                        logger.error("No expected response variables provided")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating experiment data: {e}")
            return False
    
    def _cache_suggestion(self, key: str, suggestion: Any) -> None:
        """Cache a suggestion for potential reuse."""
        try:
            with self._lock:
                self._suggestion_cache[key] = {
                    "suggestion": suggestion,
                    "timestamp": time.time()
                }
                self._last_suggestion_time = time.time()
        except Exception as e:
            logger.debug(f"Error caching suggestion: {e}")
    
    def _get_cached_suggestions(self, key: str, max_age: float = 300) -> Optional[Any]:
        """Get cached suggestions if they're not too old."""
        try:
            with self._lock:
                if key in self._suggestion_cache:
                    cached_data = self._suggestion_cache[key]
                    age = time.time() - cached_data["timestamp"]
                    if age <= max_age:
                        return cached_data["suggestion"]
                    else:
                        # Remove expired entry
                        del self._suggestion_cache[key]
            return None
        except Exception as e:
            logger.debug(f"Error getting cached suggestions: {e}")
            return None
    
    def _clear_suggestion_cache(self) -> None:
        """Clear all cached suggestions."""
        try:
            with self._lock:
                self._suggestion_cache.clear()
            logger.debug("Suggestion cache cleared")
        except Exception as e:
            logger.debug(f"Error clearing suggestion cache: {e}")
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._clear_suggestion_cache()
        logger.info("OptimizationController cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            with self._lock:
                return {
                    "cached_suggestions": len(self._suggestion_cache),
                    "last_suggestion_time": self._last_suggestion_time,
                    "cache_keys": list(self._suggestion_cache.keys())
                }
        except Exception:
            return {"cached_suggestions": 0}