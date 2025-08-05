"""
Model Manager - Specialized Gaussian Process Model Management Module

This module provides a dedicated system for building, training, and managing
Gaussian Process models in the multi-objective Bayesian optimization framework.
It separates model-related operations from the main optimizer for better 
performance, maintainability, and modularity.

Key Features:
- Efficient GP model building and training
- Model caching and reuse strategies
- Parallel model training for multiple objectives
- Advanced kernel selection and hyperparameter optimization
- Memory-efficient model storage and retrieval
- Thread-safe model operations

Classes:
    ModelManager: Main model management engine
    ModelCache: Caching system for trained models
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
from botorch.fit import fit_gpytorch_mll
from botorch.models import ModelListGP, SingleTaskGP
from botorch.models.transforms.input import Normalize
from botorch.models.transforms.outcome import Standardize
from gpytorch.kernels import MaternKernel, ScaleKernel
from gpytorch.likelihoods import GaussianLikelihood
from gpytorch.mlls import ExactMarginalLogLikelihood
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, WhiteKernel

logger = logging.getLogger(__name__)

# Constants for model configuration
MIN_DATA_POINTS_FOR_GP = 3
DEFAULT_KERNEL_TYPE = "matern"
DEFAULT_NU = 2.5


class ModelCache:
    """
    Caching system for trained Gaussian Process models to improve performance.
    """
    
    def __init__(self, max_cache_size: int = 10):
        """
        Initialize model cache.
        
        Args:
            max_cache_size: Maximum number of models to cache
        """
        self.max_cache_size = max_cache_size
        self._cache = {}
        self._access_times = {}
        self._lock = threading.Lock()
        
    def get(self, cache_key: str) -> Optional[Any]:
        """Get model from cache if available."""
        with self._lock:
            if cache_key in self._cache:
                self._access_times[cache_key] = time.time()
                return self._cache[cache_key]
            return None
    
    def put(self, cache_key: str, model: Any) -> None:
        """Store model in cache."""
        with self._lock:
            # Remove oldest models if cache is full
            if len(self._cache) >= self.max_cache_size:
                oldest_key = min(self._access_times.keys(), 
                               key=lambda k: self._access_times[k])
                del self._cache[oldest_key]
                del self._access_times[oldest_key]
            
            self._cache[cache_key] = model
            self._access_times[cache_key] = time.time()
    
    def clear(self) -> None:
        """Clear all cached models."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)


class ModelManager:
    """
    Specialized manager for Gaussian Process model operations in Bayesian optimization.
    
    This class handles all aspects of model management including building, training,
    caching, and prediction with GP models. It supports both BoTorch and scikit-learn
    backends for different use cases.
    """
    
    def __init__(
        self, 
        device: torch.device = None, 
        dtype: torch.dtype = torch.double,
        enable_caching: bool = True,
        cache_size: int = 10
    ):
        """
        Initialize the model manager.
        
        Args:
            device: PyTorch device for model computations
            dtype: Data type for tensor operations
            enable_caching: Whether to enable model caching
            cache_size: Maximum number of models to cache
        """
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = dtype
        self.enable_caching = enable_caching
        
        # Initialize model cache
        self.cache = ModelCache(cache_size) if enable_caching else None
        
        # Model storage
        self._models = {}
        self._lock = threading.Lock()
        
        logger.info(f"ModelManager initialized on {self.device} with caching={'enabled' if enable_caching else 'disabled'}")
    
    def build_botorch_models(
        self, 
        train_X: torch.Tensor, 
        train_Y: torch.Tensor, 
        objective_names: List[str]
    ) -> Optional[Union[SingleTaskGP, ModelListGP]]:
        """
        Build and fit BoTorch Gaussian Process models for each objective.
        
        Args:
            train_X: Training input tensor [n_samples, n_features]
            train_Y: Training output tensor [n_samples, n_objectives]
            objective_names: Names of the objectives
            
        Returns:
            Fitted GP model(s) or None if building fails
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(train_X, train_Y, "botorch")
            if self.enable_caching:
                cached_model = self.cache.get(cache_key)
                if cached_model is not None:
                    logger.debug("Using cached BoTorch model")
                    return cached_model
            
            # Validate input data
            if train_X.shape[0] == 0 or train_Y.shape[0] == 0:
                logger.warning("Empty training data for model building")
                return None
                
            if train_X.shape[0] < MIN_DATA_POINTS_FOR_GP:
                logger.warning(f"Insufficient data points ({train_X.shape[0]}) for GP model building")
                return None

            models = []
            
            for i, obj_name in enumerate(objective_names):
                if i >= train_Y.shape[1]:
                    logger.warning(f"Objective index {i} exceeds training data dimensions for {obj_name}")
                    continue

                Y_obj = train_Y[:, i]

                # Filter out non-finite values for the current objective
                finite_mask = torch.isfinite(Y_obj)
                if finite_mask.sum() < MIN_DATA_POINTS_FOR_GP:
                    logger.warning(f"Insufficient finite data points ({finite_mask.sum()}) for objective {obj_name}")
                    continue

                X_filtered = train_X[finite_mask]
                Y_filtered = Y_obj[finite_mask].unsqueeze(-1)

                # Build model with optimized configuration
                model = self._create_single_task_gp(X_filtered, Y_filtered)
                
                # Fit the GP model
                mll = ExactMarginalLogLikelihood(model.likelihood, model)
                fit_gpytorch_mll(mll)

                models.append(model)
                logger.debug(f"Built BoTorch model for objective '{obj_name}'")

            if not models:
                logger.warning("No GP models could be built for any objective")
                return None

            # Return appropriate model structure
            final_model = ModelListGP(*models) if len(models) > 1 else models[0]
            
            # Cache the model
            if self.enable_caching:
                self.cache.put(cache_key, final_model)
            
            logger.info(f"Successfully built {len(models)} BoTorch GP models")
            return final_model

        except Exception as e:
            logger.error(f"Error building BoTorch models: {e}", exc_info=True)
            return None
    
    def build_sklearn_models(
        self, 
        X_data: np.ndarray, 
        Y_data: Dict[str, np.ndarray],
        objective_names: List[str]
    ) -> Dict[str, GaussianProcessRegressor]:
        """
        Build scikit-learn Gaussian Process models for each objective.
        
        Args:
            X_data: Training input data [n_samples, n_features]
            Y_data: Dictionary mapping objective names to output arrays
            objective_names: Names of the objectives
            
        Returns:
            Dictionary mapping objective names to fitted GP models
        """
        models_dict = {}
        
        try:
            for obj_name in objective_names:
                if obj_name not in Y_data:
                    logger.warning(f"No data available for objective '{obj_name}'")
                    continue
                
                y_obj = Y_data[obj_name]
                
                # Filter finite values
                finite_mask = np.isfinite(y_obj)
                if np.sum(finite_mask) < MIN_DATA_POINTS_FOR_GP:
                    logger.warning(f"Insufficient data for objective '{obj_name}'")
                    continue
                
                X_filtered = X_data[finite_mask]
                y_filtered = y_obj[finite_mask]
                
                # Check cache
                cache_key = self._generate_cache_key(X_filtered, y_filtered, f"sklearn_{obj_name}")
                if self.enable_caching:
                    cached_model = self.cache.get(cache_key)
                    if cached_model is not None:
                        models_dict[obj_name] = cached_model
                        logger.debug(f"Using cached sklearn model for '{obj_name}'")
                        continue
                
                # Create and fit model
                kernel = self._create_sklearn_kernel(X_filtered.shape[1])
                
                gp = GaussianProcessRegressor(
                    kernel=kernel,
                    n_restarts_optimizer=5,
                    alpha=1e-6,
                    normalize_y=True
                )
                
                gp.fit(X_filtered, y_filtered)
                models_dict[obj_name] = gp
                
                # Cache the model
                if self.enable_caching:
                    self.cache.put(cache_key, gp)
                
                logger.debug(f"Built sklearn GP model for objective '{obj_name}'")
            
            logger.info(f"Successfully built {len(models_dict)} sklearn GP models")
            return models_dict
            
        except Exception as e:
            logger.error(f"Error building sklearn models: {e}", exc_info=True)
            return {}
    
    def predict_with_botorch_model(
        self, 
        model: Union[SingleTaskGP, ModelListGP], 
        X_test: torch.Tensor,
        objective_names: List[str],
        return_std: bool = True
    ) -> Dict[str, Dict[str, float]]:
        """
        Make predictions using BoTorch models.
        
        Args:
            model: Trained BoTorch model
            X_test: Test input tensor
            objective_names: Names of objectives
            return_std: Whether to return standard deviations
            
        Returns:
            Dictionary with predictions for each objective
        """
        predictions = {}
        
        try:
            if isinstance(model, ModelListGP):
                # Multiple objectives
                for i, obj_name in enumerate(objective_names):
                    if i < len(model.models):
                        obj_model = model.models[i]
                        with torch.no_grad():
                            posterior = obj_model.posterior(X_test)
                            mean = posterior.mean.squeeze().cpu().numpy()
                            
                            if return_std:
                                std = posterior.variance.sqrt().squeeze().cpu().numpy()
                                predictions[obj_name] = {
                                    "mean": mean,
                                    "std": std,
                                    "lower_ci": mean - 1.96 * std,
                                    "upper_ci": mean + 1.96 * std
                                }
                            else:
                                predictions[obj_name] = {"mean": mean}
            else:
                # Single objective
                obj_name = objective_names[0] if objective_names else "objective"
                with torch.no_grad():
                    posterior = model.posterior(X_test)
                    mean = posterior.mean.squeeze().cpu().numpy()
                    
                    if return_std:
                        std = posterior.variance.sqrt().squeeze().cpu().numpy()
                        predictions[obj_name] = {
                            "mean": mean,
                            "std": std,
                            "lower_ci": mean - 1.96 * std,
                            "upper_ci": mean + 1.96 * std
                        }
                    else:
                        predictions[obj_name] = {"mean": mean}
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error making predictions with BoTorch model: {e}")
            return {}
    
    def predict_with_sklearn_models(
        self, 
        models_dict: Dict[str, GaussianProcessRegressor], 
        X_test: np.ndarray,
        return_std: bool = True
    ) -> Dict[str, Dict[str, np.ndarray]]:
        """
        Make predictions using scikit-learn models.
        
        Args:
            models_dict: Dictionary of trained sklearn models
            X_test: Test input data
            return_std: Whether to return standard deviations
            
        Returns:
            Dictionary with predictions for each objective
        """
        predictions = {}
        
        try:
            for obj_name, model in models_dict.items():
                if return_std:
                    mean, std = model.predict(X_test, return_std=True)
                    predictions[obj_name] = {
                        "mean": mean,
                        "std": std,
                        "lower_ci": mean - 1.96 * std,
                        "upper_ci": mean + 1.96 * std
                    }
                else:
                    mean = model.predict(X_test)
                    predictions[obj_name] = {"mean": mean}
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error making predictions with sklearn models: {e}")
            return {}
    
    def get_feature_importances(
        self, 
        model: Union[SingleTaskGP, GaussianProcessRegressor], 
        param_names: List[str]
    ) -> Dict[str, float]:
        """
        Extract feature importances from GP model.
        
        Args:
            model: Trained GP model
            param_names: Names of parameters/features
            
        Returns:
            Dictionary mapping parameter names to importance scores
        """
        try:
            importances = {}
            
            if isinstance(model, SingleTaskGP):
                # BoTorch model
                if (hasattr(model.covar_module, "base_kernel") and 
                    hasattr(model.covar_module.base_kernel, "lengthscale")):
                    
                    lengthscales = (
                        model.covar_module.base_kernel.lengthscale.squeeze()
                        .detach().cpu().numpy()
                    )
                    
                    # Inverse of lengthscales represents importance
                    importance_scores = 1.0 / lengthscales
                    
                    # Normalize to sum to 1
                    if np.sum(importance_scores) > 0:
                        importance_scores = importance_scores / np.sum(importance_scores)
                    
                    for i, param_name in enumerate(param_names):
                        if i < len(importance_scores):
                            importances[param_name] = float(importance_scores[i])
            
            elif isinstance(model, GaussianProcessRegressor):
                # Scikit-learn model
                if hasattr(model.kernel_, "length_scale"):
                    length_scales = np.atleast_1d(model.kernel_.length_scale)
                    importance_scores = 1.0 / length_scales
                    
                    # Normalize
                    if np.sum(importance_scores) > 0:
                        importance_scores = importance_scores / np.sum(importance_scores)
                    
                    for i, param_name in enumerate(param_names):
                        if i < len(importance_scores):
                            importances[param_name] = float(importance_scores[i])
            
            return importances
            
        except Exception as e:
            logger.error(f"Error extracting feature importances: {e}")
            return {}
    
    def _create_single_task_gp(self, X: torch.Tensor, Y: torch.Tensor) -> SingleTaskGP:
        """Create a SingleTaskGP model with optimal configuration."""
        return SingleTaskGP(
            train_X=X,
            train_Y=Y,
            covar_module=ScaleKernel(
                MaternKernel(nu=DEFAULT_NU, ard_num_dims=X.shape[-1])
            ),
            input_transform=Normalize(d=X.shape[-1]),
            outcome_transform=Standardize(m=1),
        )
    
    def _create_sklearn_kernel(self, n_dims: int):
        """Create an optimized kernel for scikit-learn GP."""
        return Matern(length_scale=0.5, nu=DEFAULT_NU) + WhiteKernel(noise_level=0.01)
    
    def _generate_cache_key(self, X: Union[torch.Tensor, np.ndarray], Y: Union[torch.Tensor, np.ndarray], prefix: str) -> str:
        """Generate a cache key for model storage."""
        try:
            if isinstance(X, torch.Tensor):
                X_bytes = X.cpu().numpy().tobytes()
            else:
                X_bytes = X.tobytes()
                
            if isinstance(Y, torch.Tensor):
                Y_bytes = Y.cpu().numpy().tobytes()
            else:
                Y_bytes = Y.tobytes()
                
            return f"{prefix}_{hash(X_bytes + Y_bytes)}"
        except Exception:
            return f"{prefix}_{int(time.time() * 1000000)}"
    
    def clear_cache(self) -> None:
        """Clear all cached models."""
        if self.cache:
            self.cache.clear()
        logger.info("Model cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        if self.cache:
            return {"cache_size": self.cache.size()}
        return {"cache_size": 0}
    
    def set_models(self, models: Dict[str, Any]) -> None:
        """Store models in the manager."""
        with self._lock:
            self._models.update(models)
    
    def get_models(self) -> Dict[str, Any]:
        """Retrieve all stored models."""
        with self._lock:
            return self._models.copy()
    
    def get_model(self, name: str) -> Optional[Any]:
        """Retrieve a specific model by name."""
        with self._lock:
            return self._models.get(name)