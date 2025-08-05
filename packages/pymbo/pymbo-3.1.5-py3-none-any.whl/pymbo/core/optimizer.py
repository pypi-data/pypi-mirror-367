"""
Optimizer Engine - Enhanced Multi-Objective Bayesian Optimization

This module implements a sophisticated multi-objective Bayesian optimization engine
using PyTorch/BoTorch for the Multi-Objective Optimization Laboratory. It provides
advanced optimization capabilities with robust error handling and comprehensive
functionality.

Key Features:
- Multi-objective Bayesian optimization with Gaussian Process models
- Expected Hypervolume Improvement acquisition function
- Support for continuous and categorical parameters
- Latin Hypercube and random initial sampling
- Pareto front computation and hypervolume metrics
- Advanced constraint handling and validation
- Thread-safe operations with comprehensive logging
- Performance optimization and caching

Classes:
    SimpleParameterTransformer: Handles parameter space transformations
    EnhancedMultiObjectiveOptimizer: Main optimization engine

Author: Multi-Objective Optimization Laboratory
Version: 3.1.5 Enhanced
"""

import ast
import logging
import operator as op
import re
import time
import warnings
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Scientific computing imports
import numpy as np
import pandas as pd

# Performance optimization imports
try:
    from pymbo.utils.performance_optimizer import (
        performance_timer, DataHasher, LazyLoader, MemoryManager
    )
    PERFORMANCE_OPTIMIZATION_AVAILABLE = True
except ImportError:
    PERFORMANCE_OPTIMIZATION_AVAILABLE = False

# PyTorch and BoTorch imports for Bayesian optimization
import torch
from torch import Tensor

# BoTorch components for multi-objective optimization
from botorch.acquisition.analytic import LogExpectedImprovement, UpperConfidenceBound
from botorch.acquisition.multi_objective import ExpectedHypervolumeImprovement
from botorch.fit import fit_gpytorch_mll
from botorch.models import ModelListGP, SingleTaskGP
from botorch.models.transforms.input import Normalize
from botorch.models.transforms.outcome import Standardize
from botorch.optim import optimize_acqf
from botorch.utils.multi_objective.box_decompositions.non_dominated import (
    FastNondominatedPartitioning,
)
from botorch.utils.multi_objective.pareto import is_non_dominated
from botorch.utils.sampling import draw_sobol_samples
from botorch.utils.transforms import normalize, unnormalize

# GPyTorch components for Gaussian Process models
from gpytorch.kernels import MaternKernel, ScaleKernel
from gpytorch.likelihoods import GaussianLikelihood
from gpytorch.mlls import ExactMarginalLogLikelihood

# Additional scientific libraries
from scipy.stats import qmc  # Latin Hypercube Sampling
from sklearn.preprocessing import StandardScaler

# Configure warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning, module="botorch")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="botorch")
warnings.filterwarnings("ignore", category=UserWarning, module="gpytorch")

# Initialize logger
logger = logging.getLogger(__name__)

# Optimization configuration constants
MIN_DATA_POINTS_FOR_GP = 3  # Minimum data points required for GP model training
DEFAULT_BATCH_SIZE = 5      # Default number of suggestions to generate
MAX_BATCH_SIZE = 50         # Maximum allowed batch size
DEFAULT_NUM_RESTARTS = 10   # Default number of optimization restarts
DEFAULT_RAW_SAMPLES = 100   # Default number of raw samples for optimization
MAX_ITERATIONS = 1000       # Maximum iterations for acquisition optimization

# Numerical constants
EPS = 1e-8                  # Small epsilon for numerical stability
INF = 1e6                   # Large number for constraint handling

# Security: Allowed operators for safe constraint expression evaluation
# This prevents code injection through constraint strings
ALLOWED_CONSTRAINT_OPERATORS = {"+", "-", "*", "/", "(", ")", "<", ">", "=", " "}
ALLOWED_CONSTRAINT_FUNCTIONS = {"abs", "sqrt", "log", "exp", "sin", "cos", "tan"}


def validate_constraint_expression(constraint: str, param_names: List[str]) -> bool:
    """
    Validates a constraint expression for security and correctness.

    Args:
        constraint: The constraint expression to validate
        param_names: List of valid parameter names

    Returns:
        bool: True if constraint is safe, False otherwise
    """
    if not isinstance(constraint, str):
        return False

    # Remove whitespace for easier processing
    clean_constraint = constraint.replace(" ", "")

    # Check for dangerous patterns
    dangerous_patterns = [
        "import",
        "exec",
        "eval",
        "__",
        "getattr",
        "setattr",
        "delattr",
    ]
    if any(pattern in constraint.lower() for pattern in dangerous_patterns):
        logger.warning(f"Dangerous pattern detected in constraint: {constraint}")
        return False

    # Check that only allowed characters are present
    allowed_chars = (
        ALLOWED_CONSTRAINT_OPERATORS | set("0123456789.") | set("".join(param_names))
    )
    for char in clean_constraint:
        if char not in allowed_chars and not char.isalpha():
            logger.warning(f"Disallowed character '{char}' in constraint: {constraint}")
            return False

    # Basic syntax validation using AST
    try:
        # Replace parameter names with dummy values for parsing
        test_expr = clean_constraint
        for param in param_names:
            test_expr = test_expr.replace(param, "1.0")

        # Try to parse as AST to check basic syntax
        ast.parse(test_expr, mode="eval")
        return True
    except (SyntaxError, ValueError) as e:
        logger.warning(f"Invalid syntax in constraint '{constraint}': {e}")
        return False


class SimpleParameterTransformer:
    """
    Transforms parameters between their original scale/representation and a normalized
    tensor representation (typically [0, 1]) suitable for Bayesian optimization models.
    Handles continuous, discrete, and categorical parameter types.
    """

    def __init__(self, params_config: Dict[str, Dict[str, Any]]):
        """
        Initializes the transformer with parameter configurations.

        Args:
            params_config: A dictionary where keys are parameter names and values
                           are dictionaries containing 'type' (e.g., 'continuous',
                           'discrete', 'categorical') and 'bounds' or 'values'.
        """
        self.params_config = params_config
        self.param_names = list(params_config.keys())
        self.n_params = len(self.param_names)

        # Stores the min/max bounds for each parameter in its normalized space.
        # For continuous/discrete, these are the actual bounds.
        # For categorical, these are 0 to num_categories - 1.
        self.bounds = []
        # Stores mappings for categorical parameters (value -> integer index).
        self.categorical_mappings = {}

        # Iterate through each parameter to set up its transformation rules and bounds.
        for i, (name, config) in enumerate(params_config.items()):
            param_type = config["type"]

            if param_type in ["continuous", "discrete"]:
                bounds = config["bounds"]
                self.bounds.append([float(bounds[0]), float(bounds[1])])
            elif param_type == "categorical":
                values = config["values"]
                self.categorical_mappings[i] = {v: j for j, v in enumerate(values)}
                self.bounds.append([0.0, float(len(values) - 1)])
            else:
                self.bounds.append([0.0, 1.0])

        # Convert to tensor
        self.bounds_tensor = torch.tensor(self.bounds, dtype=torch.double)

        logger.info(f"Parameter transformer initialized for {self.n_params} parameters")

    def params_to_tensor(self, params_dict: Dict[str, Any]) -> torch.Tensor:
        """
        Converts a dictionary of parameters to a normalized PyTorch tensor.
        Continuous and discrete parameters are normalized to [0, 1].
        Categorical parameters are mapped to their integer index and then normalized.

        Args:
            params_dict: A dictionary where keys are parameter names and values
                         are their corresponding experimental values.

        Returns:
            A `torch.Tensor` of shape (n_params,) with normalized parameter values.
            Returns a tensor of zeros if an error occurs during conversion.
        """
        try:
            values = []
            for i, name in enumerate(self.param_names):
                value = params_dict.get(name, 0)  # Default to 0 if parameter not found
                config = self.params_config[name]
                param_type = config["type"]

                if param_type in ["continuous", "discrete"]:
                    bounds = self.bounds[i]
                    normalized = (float(value) - bounds[0]) / (bounds[1] - bounds[0])
                elif param_type == "categorical":
                    values_list = config["values"]
                    try:
                        idx = values_list.index(value)
                        normalized = (
                            float(idx) / (len(values_list) - 1)
                            if len(values_list) > 1
                            else 0.0
                        )
                    except ValueError:
                        normalized = 0.0
                else:
                    normalized = float(value)

                values.append(max(0.0, min(1.0, normalized)))

            return torch.tensor(values, dtype=torch.double)
        except Exception as e:
            logger.error(f"Error converting params to tensor: {e}")
            return torch.zeros(self.n_params, dtype=torch.double)

    def tensor_to_params(self, tensor: torch.Tensor) -> Dict[str, Any]:
        """
        Converts a normalized PyTorch tensor back to a dictionary of parameters
        in their original scale/representation.

        Args:
            tensor: A `torch.Tensor` of shape (n_params,) with normalized parameter values.

        Returns:
            A dictionary where keys are parameter names and values are their
            corresponding values in the original scale.
            Returns a dictionary with default values (0) if an error occurs.
        """
        try:
            tensor = tensor.clamp(0, 1)  # Ensure values are within [0, 1] range
            params_dict = {}

            for i, name in enumerate(self.param_names):
                value = tensor[i].item()
                config = self.params_config[name]
                param_type = config["type"]

                if param_type == "continuous":
                    bounds = self.bounds[i]
                    actual_value = bounds[0] + value * (bounds[1] - bounds[0])
                    if "precision" in config and config["precision"] is not None:
                        actual_value = round(actual_value, config["precision"])
                    params_dict[name] = actual_value
                elif param_type == "discrete":
                    bounds = self.bounds[i]
                    actual_value = int(bounds[0] + value * (bounds[1] - bounds[0]))
                    params_dict[name] = actual_value
                elif param_type == "categorical":
                    values_list = config["values"]
                    idx = min(
                        int(round(value * (len(values_list) - 1))), len(values_list) - 1
                    )
                    params_dict[name] = values_list[idx]
                else:
                    params_dict[name] = value

            return params_dict
        except Exception as e:
            logger.error(f"Error converting tensor to params: {e}")
            return {name: 0 for name in self.param_names}


class EnhancedMultiObjectiveOptimizer:
    """
    Simplified multi-objective Bayesian optimizer that actually works
    """

    def __init__(
        self,
        params_config: Dict[str, Dict[str, Any]],
        responses_config: Dict[str, Dict[str, Any]],
        general_constraints: Optional[List[str]] = None,
        random_seed: Optional[int] = None,
        initial_sampling_method: str = "random",
        num_restarts: int = 10,
        raw_samples: int = 100,
        **kwargs,
    ):
        """
        Initializes the EnhancedMultiObjectiveOptimizer.

        Args:
            params_config: Configuration for input parameters, including their type,
                           bounds/values, and optional optimization goals.
            responses_config: Configuration for response variables (objectives),
                              including their names and optimization goals (Maximize/Minimize).
            general_constraints: Optional list of string representations of general
                                 constraints (e.g., "x1 + x2 <= 10"). Not fully implemented
                                 in this simplified version but kept for future expansion.
            random_seed: Optional integer to seed the random number generators for
                         reproducibility.
            initial_sampling_method: Method to use for initial data generation when
                                     insufficient experimental data is available.
                                     Currently supports "random" and "LHS" (Latin Hypercube Sampling).
            **kwargs: Additional keyword arguments (e.g., for device configuration).
        """
        self.params_config = params_config
        self.responses_config = responses_config
        self.general_constraints = general_constraints or []

        # Cache for hypervolume data to avoid recalculation on load
        self._cached_hypervolume_data = {}

        # Determine the device (GPU if available, otherwise CPU) for PyTorch operations.
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Set the default data type for PyTorch tensors to double precision.
        self.dtype = torch.double
        # Store the chosen initial sampling method.
        self.initial_sampling_method = initial_sampling_method
        self.num_restarts = num_restarts
        self.raw_samples = raw_samples

        # Apply random seed for reproducibility if provided.
        if random_seed is not None:
            torch.manual_seed(random_seed)
            np.random.seed(random_seed)

        # Initialize core components of the optimizer.
        self.parameter_transformer = SimpleParameterTransformer(params_config)

        # Set up the optimization objectives based on the responses_config.
        self._setup_objectives()

        # Initialize data structures for storing experimental data and iteration history.
        self._initialize_data_storage()

        logger.info(f"Multi-objective optimizer initialized on {self.device}")

    def _setup_objectives(self) -> None:
        """
        Sets up the objective names and their optimization directions (maximize/minimize)
        based on the `responses_config` and `params_config`.
        """
        self.objective_names = []
        self.objective_directions = []  # 1 for maximize, -1 for minimize

        # Process responses defined as objectives
        for name, config in self.responses_config.items():
            goal = config.get("goal", "None")
            if goal in ["Maximize", "Minimize"]:
                self.objective_names.append(name)
                self.objective_directions.append(1 if goal == "Maximize" else -1)

        # Process parameters that might also be objectives (less common but supported)
        for name, config in self.params_config.items():
            goal = config.get("goal", "None")
            if goal in ["Maximize", "Minimize"]:
                self.objective_names.append(name)
                self.objective_directions.append(1 if goal == "Maximize" else -1)

        logger.info(
            f"Setup {len(self.objective_names)} objectives: {self.objective_names}"
        )

        if not self.objective_names:
            raise ValueError("At least one optimization objective must be defined.")

    def _initialize_data_storage(self) -> None:
        """
        Initializes the data storage attributes for experimental data, iteration history,
        and a cache for models.
        """
        self.experimental_data = (
            pd.DataFrame()
        )  # Stores all experimental data (parameters + responses)
        self.iteration_history = (
            []
        )  # Stores historical data about each optimization iteration
        self.models_cache = {}  # Cache for storing trained GP models

    def _generate_doe_samples(
        self, n_suggestions: int, method: str = "LHS"
    ) -> List[Dict[str, Any]]:
        """
        Generates initial samples using Design of Experiments (DoE) methods.
        These samples are used to seed the Bayesian optimization process when
        there is insufficient experimental data to train the GP models.

        Args:
            n_suggestions (int): The number of parameter combinations to suggest.
            method (str): The DoE method to use. Currently supports:
                          - 'LHS': Latin Hypercube Sampling.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a suggested
                                  parameter combination in its original scale.
        """
        suggestions = []
        # Get the parameter bounds from the transformer, transpose them, and move to CPU
        # for NumPy operations.
        param_bounds = self.parameter_transformer.bounds_tensor.T.cpu().numpy()

        if method == "LHS":
            # Initialize Latin Hypercube Sampler with the number of parameters.
            sampler = qmc.LatinHypercube(d=self.parameter_transformer.n_params)
            # Generate samples in the normalized [0, 1) range.
            lhs_samples_normalized = sampler.random(n=n_suggestions)

            for i in range(n_suggestions):
                # Scale the normalized samples back to the original parameter bounds.
                # Need to reshape to 2D for qmc.scale
                sample_2d = lhs_samples_normalized[i].reshape(1, -1)
                sample_scaled = qmc.scale(
                    sample_2d, param_bounds[0], param_bounds[1]
                ).flatten()

                # Convert the scaled sample to a PyTorch tensor and then to a parameter dictionary.
                sample_tensor = torch.tensor(sample_scaled, dtype=self.dtype)
                param_dict = self.parameter_transformer.tensor_to_params(sample_tensor)
                suggestions.append(param_dict)
            logger.info(
                f"Generated {len(suggestions)} initial suggestions using Latin Hypercube Sampling."
            )
        else:
            logger.warning(
                f"Unknown DoE method: {method}. Falling back to random sampling."
            )
            return self._generate_random_samples(n_suggestions)

        return suggestions

    def add_experimental_data(self, data_df: pd.DataFrame) -> None:
        """
        Adds new experimental data points to the optimizer's internal data storage.
        After adding data, it updates the training tensors, calculates the hypervolume,
        and records the iteration history.

        Args:
            data_df (pd.DataFrame): A Pandas DataFrame containing the new experimental
                                    data. It must include columns for all parameters
                                    and response variables defined in the configuration.
        Raises:
            Exception: If an error occurs during data addition or processing.
        """
        try:
            logger.info(f"Adding {len(data_df)} experimental data points")

            # Concatenate new data with existing experimental data.
            if self.experimental_data.empty:
                self.experimental_data = data_df.copy()
            else:
                self.experimental_data = pd.concat(
                    [self.experimental_data, data_df], ignore_index=True
                )

            # Update the PyTorch tensors used for training the GP models.
            self._update_training_data()

            # Calculate the current hypervolume indicator, which measures the quality
            # of the Pareto front.
            hypervolume_data = self._calculate_hypervolume()

            # Record the details of the current iteration with enhanced hypervolume data.
            iteration_record = {
                "iteration": len(self.iteration_history) + 1,
                "timestamp": pd.Timestamp.now(),
                "n_experiments": len(self.experimental_data),
                "hypervolume": hypervolume_data,
                # Keep legacy field for backward compatibility
                "hypervolume_raw": hypervolume_data.get("raw_hypervolume", 0.0),
                "hypervolume_normalized": hypervolume_data.get(
                    "normalized_hypervolume", 0.0
                ),
            }

            # Add convergence analysis if we have sufficient data
            if len(self.iteration_history) >= 3:
                convergence_info = self.check_hypervolume_convergence()
                iteration_record["convergence_analysis"] = {
                    "converged": convergence_info.get("converged", False),
                    "relative_improvement": convergence_info.get(
                        "relative_improvement", 0.0
                    ),
                    "recommendation": convergence_info.get(
                        "recommendation", "continue"
                    ),
                }

            self.iteration_history.append(iteration_record)

            logger.info(
                f"Data added successfully. Total experiments: {len(self.experimental_data)}"
            )

        except Exception as e:
            logger.error(f"Error adding experimental data: {e}")
            raise

    def _update_training_data(self) -> None:
        """
        Updates the `train_X` and `train_Y` tensors used for training the
        Gaussian Process (GP) models. `train_X` contains the normalized parameter
        values, and `train_Y` contains the objective values. For minimization
        objectives, the values in `train_Y` are negated.
        """
        if self.experimental_data.empty:
            logger.info("No experimental data to update training tensors.")
            return

        X_list = []  # List to store parameter tensors
        Y_list = []  # List to store objective tensors

        for _, row in self.experimental_data.iterrows():
            # Extract parameter values from the current row and convert to a dictionary.
            param_dict = {
                param_name: row[param_name]
                for param_name in self.parameter_transformer.param_names
            }

            # Transform the parameter dictionary into a normalized PyTorch tensor.
            X_tensor = self.parameter_transformer.params_to_tensor(param_dict)
            X_list.append(X_tensor)

            # Extract objective values from the current row.
            y_values = []
            for obj_name in self.objective_names:
                if obj_name in row:
                    value = row[obj_name]
                    # Handle cases where the response might be a list (e.g., multiple replicates)
                    if isinstance(value, list) and len(value) > 0:
                        mean_value = np.mean(value)
                    else:
                        mean_value = float(value)
                    y_values.append(mean_value)
                else:
                    # If an objective is missing for a data point, treat as NaN.
                    y_values.append(np.nan)

            # Convert objective values to a PyTorch tensor.
            Y_tensor = torch.tensor(y_values, dtype=self.dtype, device=self.device)
            Y_list.append(Y_tensor)

        if X_list and Y_list:
            # Stack the lists of tensors into single tensors for training.
            self.train_X = torch.stack(X_list).to(self.device, self.dtype)
            self.train_Y = torch.stack(Y_list).to(self.device, self.dtype)

            # Apply objective directions: negate values for minimization objectives.
            for i, direction in enumerate(self.objective_directions):
                if direction == -1:  # If objective is to be minimized
                    self.train_Y[:, i] = -self.train_Y[:, i]

            logger.info(
                f"Training data updated: X shape {self.train_X.shape}, Y shape {self.train_Y.shape}"
            )

    def _calculate_adaptive_reference_point(
        self, clean_Y: torch.Tensor
    ) -> torch.Tensor:
        """
        Calculates an adaptive reference point based on the data range for better
        hypervolume calculation across different problem scales.

        Args:
            clean_Y: Clean objective values tensor (finite values only)

        Returns:
            torch.Tensor: Adaptive reference point
        """
        min_observed_Y = clean_Y.min(dim=0)[0]
        max_observed_Y = clean_Y.max(dim=0)[0]

        # Calculate data range for each objective
        data_range = max_observed_Y - min_observed_Y

        # Use adaptive offset: minimum of 10% of data range or 1.0
        # This scales better for problems with different objective magnitudes
        adaptive_offset = torch.maximum(
            data_range * 0.1, torch.ones_like(data_range) * 0.1
        )

        # Ensure minimum offset for very small ranges
        adaptive_offset = torch.maximum(
            adaptive_offset, torch.ones_like(data_range) * 0.01
        )

        ref_point = min_observed_Y - adaptive_offset

        # Ensure the reference point does not contain NaNs
        ref_point = torch.nan_to_num(ref_point, nan=-1.0)

        logger.debug(f"Adaptive offset: {adaptive_offset}")
        logger.debug(f"Data range: {data_range}")

        return ref_point

    def _calculate_hypervolume(self) -> Dict[str, float]:
        """
        Calculates the Hypervolume Indicator (HVI) for the current set of observed
        objective values. HVI is a common metric for multi-objective optimization
        progress, representing the volume of the objective space dominated by the
        Pareto front and bounded by a reference point.

        Returns:
            Dict[str, float]: Dictionary containing 'raw_hypervolume', 'normalized_hypervolume',
                             and 'reference_point_info'. Returns dict with 0.0 values if there are
                             insufficient data points, no objectives, or if calculation fails.
        """
        default_result = {
            "raw_hypervolume": 0.0,
            "normalized_hypervolume": 0.0,
            "reference_point_adaptive": True,
            "data_points_used": 0,
        }

        try:
            # Hypervolume is meaningful for at least two objectives.
            if len(self.objective_names) < 2 or not hasattr(self, "train_Y"):
                logger.debug(
                    "Hypervolume calculation skipped: Less than 2 objectives or no training data."
                )
                return default_result

            Y = self.train_Y
            if Y.shape[0] == 0:
                logger.debug(
                    "Hypervolume calculation skipped: No data points in train_Y."
                )
                return default_result

            # Filter out rows containing NaN values, as they cannot be used for HVI calculation.
            finite_mask = torch.isfinite(Y).all(dim=1)
            if not finite_mask.any():
                logger.debug("Hypervolume calculation skipped: No finite data points.")
                return default_result

            clean_Y = Y[finite_mask]

            if clean_Y.shape[0] < 2:
                logger.debug(
                    f"Hypervolume calculation skipped: Less than 2 clean data points ({clean_Y.shape[0]}) for HVI."
                )
                return default_result

            logger.debug(f"clean_Y shape: {clean_Y.shape}")
            logger.debug(
                f"clean_Y min: {clean_Y.min(dim=0)[0]}, max: {clean_Y.max(dim=0)[0]}"
            )

            # Calculate adaptive reference point
            ref_point = self._calculate_adaptive_reference_point(clean_Y)

            # Calculate hypervolume using BoTorch's FastNondominatedPartitioning.
            try:
                logger.debug(f"Adaptive ref point for HVI: {ref_point}")
                partitioning = FastNondominatedPartitioning(
                    ref_point=ref_point, Y=clean_Y
                )
                raw_hypervolume = partitioning.compute_hypervolume().item()

                # Calculate normalized hypervolume for better interpretability
                max_observed_Y = clean_Y.max(dim=0)[0]
                theoretical_max_volume = torch.prod(max_observed_Y - ref_point)

                # Avoid division by zero
                if theoretical_max_volume.item() > 1e-12:
                    normalized_hypervolume = (
                        raw_hypervolume / theoretical_max_volume.item()
                    )
                else:
                    normalized_hypervolume = 0.0

                # Ensure normalized hypervolume is between 0 and 1
                normalized_hypervolume = max(0.0, min(1.0, normalized_hypervolume))

                result = {
                    "raw_hypervolume": raw_hypervolume,
                    "normalized_hypervolume": normalized_hypervolume,
                    "reference_point_adaptive": True,
                    "data_points_used": clean_Y.shape[0],
                }

                logger.debug(f"Raw hypervolume: {raw_hypervolume}")
                logger.debug(f"Normalized hypervolume: {normalized_hypervolume}")
                logger.debug(f"Theoretical max volume: {theoretical_max_volume.item()}")

                return result

            except Exception as e:
                logger.warning(
                    f"Hypervolume calculation failed (FastNondominatedPartitioning): {e}"
                )
                return default_result

        except Exception as e:
            logger.error(f"Error in _calculate_hypervolume: {e}", exc_info=True)
            return default_result

    def _calculate_hypervolume_legacy(self) -> float:
        """
        Legacy method that returns only the raw hypervolume for backward compatibility.
        This maintains compatibility with existing code that expects a float return.

        Returns:
            float: Raw hypervolume value
        """
        hv_result = self._calculate_hypervolume()
        return hv_result["raw_hypervolume"]

    def check_hypervolume_convergence(
        self, window_size: int = 5, threshold: float = 0.01, use_normalized: bool = True
    ) -> Dict[str, Any]:
        """
        Checks for hypervolume-based convergence using a sliding window approach.

        Args:
            window_size: Number of recent iterations to consider for convergence
            threshold: Relative change threshold below which we consider convergence
            use_normalized: Whether to use normalized hypervolume for convergence check

        Returns:
            Dict containing convergence status, metrics, and recommendations
        """
        convergence_result = {
            "converged": False,
            "progress_stagnant": False,
            "iterations_stable": 0,
            "relative_improvement": 0.0,
            "recommendation": "continue",
            "confidence": "low",
        }

        try:
            if len(self.iteration_history) < window_size:
                convergence_result["recommendation"] = "continue - insufficient data"
                return convergence_result

            # Extract hypervolume values from recent iterations
            hv_key = "normalized_hypervolume" if use_normalized else "hypervolume"

            # Handle both old format (float) and new format (dict)
            recent_hvs = []
            for iteration in self.iteration_history[-window_size:]:
                hv_value = iteration.get("hypervolume", 0.0)
                if isinstance(hv_value, dict):
                    recent_hvs.append(hv_value.get(hv_key, 0.0))
                else:
                    # Legacy format - use raw value
                    recent_hvs.append(hv_value)

            if not recent_hvs or all(hv == 0.0 for hv in recent_hvs):
                convergence_result["recommendation"] = (
                    "continue - no valid hypervolume data"
                )
                return convergence_result

            # Calculate relative improvement
            max_hv = max(recent_hvs)
            min_hv = min(recent_hvs)

            if max_hv > 1e-12:
                relative_improvement = (max_hv - min_hv) / max_hv
            else:
                relative_improvement = 0.0

            convergence_result["relative_improvement"] = relative_improvement

            # Check for convergence
            if relative_improvement < threshold:
                convergence_result["converged"] = True
                convergence_result["iterations_stable"] = window_size
                convergence_result["confidence"] = (
                    "high" if window_size >= 10 else "medium"
                )

                # Additional check: is hypervolume actually improving over longer period?
                if len(self.iteration_history) >= window_size * 2:
                    earlier_hvs = []
                    for iteration in self.iteration_history[
                        -(window_size * 2) : -window_size
                    ]:
                        hv_value = iteration.get("hypervolume", 0.0)
                        if isinstance(hv_value, dict):
                            earlier_hvs.append(hv_value.get(hv_key, 0.0))
                        else:
                            earlier_hvs.append(hv_value)

                    if earlier_hvs and max(earlier_hvs) > 1e-12:
                        long_term_improvement = (
                            max(recent_hvs) - max(earlier_hvs)
                        ) / max(earlier_hvs)

                        if long_term_improvement < threshold / 2:
                            convergence_result["progress_stagnant"] = True
                            convergence_result["recommendation"] = "consider_stopping"
                        else:
                            convergence_result["recommendation"] = "continue_cautiously"
                    else:
                        convergence_result["recommendation"] = "continue_cautiously"
                else:
                    convergence_result["recommendation"] = "continue_cautiously"
            else:
                convergence_result["recommendation"] = "continue"

            # Calculate trend
            if len(recent_hvs) >= 3:
                # Simple linear trend analysis
                x = list(range(len(recent_hvs)))
                n = len(recent_hvs)
                sum_x = sum(x)
                sum_y = sum(recent_hvs)
                sum_xy = sum(xi * yi for xi, yi in zip(x, recent_hvs))
                sum_x2 = sum(xi * xi for xi in x)

                if n * sum_x2 - sum_x * sum_x != 0:
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                    convergence_result["trend_slope"] = slope

                    if slope < -threshold / 10:
                        convergence_result["recommendation"] = "investigate_degradation"

            logger.debug(f"Convergence check: {convergence_result}")
            return convergence_result

        except Exception as e:
            logger.error(f"Error in convergence check: {e}", exc_info=True)
            convergence_result["recommendation"] = "continue - error in analysis"
            return convergence_result

    def get_optimization_progress_summary(self) -> Dict[str, Any]:
        """
        Provides a comprehensive summary of optimization progress including
        hypervolume trends, convergence status, and recommendations.

        Returns:
            Dict containing detailed progress analysis
        """
        summary = {
            "total_iterations": len(self.iteration_history),
            "total_experiments": (
                len(self.experimental_data) if hasattr(self, "experimental_data") else 0
            ),
            "current_hypervolume": None,
            "hypervolume_trend": "unknown",
            "convergence_status": "unknown",
            "efficiency_metrics": {},
            "recommendations": [],
        }

        try:
            if not self.iteration_history:
                summary["recommendations"].append(
                    "Start optimization by adding experimental data"
                )
                return summary

            # Get current hypervolume
            latest_iteration = self.iteration_history[-1]
            hv_value = latest_iteration.get("hypervolume", 0.0)

            if isinstance(hv_value, dict):
                summary["current_hypervolume"] = {
                    "raw": hv_value.get("raw_hypervolume", 0.0),
                    "normalized": hv_value.get("normalized_hypervolume", 0.0),
                    "data_points_used": hv_value.get("data_points_used", 0),
                }
            else:
                summary["current_hypervolume"] = {"raw": hv_value, "normalized": None}

            # Analyze trend over recent iterations
            if len(self.iteration_history) >= 3:
                recent_iterations = min(10, len(self.iteration_history))
                recent_hvs = []

                for iteration in self.iteration_history[-recent_iterations:]:
                    hv_val = iteration.get("hypervolume", 0.0)
                    if isinstance(hv_val, dict):
                        recent_hvs.append(hv_val.get("raw_hypervolume", 0.0))
                    else:
                        recent_hvs.append(hv_val)

                if len(recent_hvs) >= 3 and max(recent_hvs) > 1e-12:
                    first_third = sum(recent_hvs[: len(recent_hvs) // 3]) / (
                        len(recent_hvs) // 3
                    )
                    last_third = sum(recent_hvs[-len(recent_hvs) // 3 :]) / (
                        len(recent_hvs) // 3
                    )

                    relative_change = (last_third - first_third) / max(
                        first_third, 1e-12
                    )

                    if relative_change > 0.05:
                        summary["hypervolume_trend"] = "improving"
                    elif relative_change > -0.02:
                        summary["hypervolume_trend"] = "stable"
                    else:
                        summary["hypervolume_trend"] = "declining"

            # Check convergence
            convergence_result = self.check_hypervolume_convergence()
            summary["convergence_status"] = convergence_result["recommendation"]
            summary["convergence_details"] = convergence_result

            # Calculate efficiency metrics
            if len(self.iteration_history) > 1:
                # Hypervolume per experiment efficiency
                current_hv = (
                    summary["current_hypervolume"]["raw"]
                    if summary["current_hypervolume"]
                    else 0.0
                )
                experiments_count = summary["total_experiments"]

                if experiments_count > 0:
                    summary["efficiency_metrics"]["hv_per_experiment"] = (
                        current_hv / experiments_count
                    )

                # Rate of improvement
                if len(self.iteration_history) >= 5:
                    early_hv = self.iteration_history[
                        min(4, len(self.iteration_history) - 1)
                    ].get("hypervolume", 0.0)
                    if isinstance(early_hv, dict):
                        early_hv = early_hv.get("raw_hypervolume", 0.0)

                    if early_hv > 1e-12:
                        improvement_rate = (current_hv - early_hv) / early_hv
                        summary["efficiency_metrics"][
                            "improvement_rate"
                        ] = improvement_rate

            # Generate recommendations
            if summary["hypervolume_trend"] == "declining":
                summary["recommendations"].append(
                    "Check for overfitting or data quality issues"
                )
            elif (
                summary["hypervolume_trend"] == "stable"
                and len(self.iteration_history) > 10
            ):
                summary["recommendations"].append(
                    "Consider exploring different regions of parameter space"
                )
            elif convergence_result["converged"]:
                summary["recommendations"].append(
                    "Optimization may have converged - consider validation experiments"
                )
            else:
                summary["recommendations"].append(
                    "Continue optimization - good progress being made"
                )

            return summary

        except Exception as e:
            logger.error(f"Error generating progress summary: {e}", exc_info=True)
            summary["recommendations"].append(
                "Error in progress analysis - continue with caution"
            )
            return summary

    def get_cached_hypervolume_data(self) -> Dict[str, Any]:
        """Get cached hypervolume data if available, otherwise calculate fresh"""
        if self._cached_hypervolume_data:
            logger.info("Using cached hypervolume data")
            return self._cached_hypervolume_data
        else:
            logger.info("No cached hypervolume data found, calculating fresh")
            try:
                current_hv = self._calculate_hypervolume()
                progress_summary = self.get_optimization_progress_summary()
                convergence_data = self.check_hypervolume_convergence()

                return {
                    "current_hypervolume": current_hv,
                    "progress_summary": progress_summary,
                    "convergence_analysis": convergence_data,
                    "calculation_timestamp": pd.Timestamp.now().isoformat(),
                }
            except Exception as e:
                logger.error(f"Error calculating hypervolume data: {e}")
                return {}

    def set_cached_hypervolume_data(self, cached_data: Dict[str, Any]):
        """Set cached hypervolume data (used when loading from file)"""
        self._cached_hypervolume_data = cached_data
        logger.info("Cached hypervolume data has been set")

    @performance_timer if PERFORMANCE_OPTIMIZATION_AVAILABLE else lambda x: x
    def suggest_next_experiment(self, n_suggestions: int = 1) -> List[Dict[str, Any]]:
        """
        Generates suggestions for the next set of experiments using Bayesian optimization.
        If insufficient data is available, it falls back to initial sampling methods
        (e.g., random or Latin Hypercube Sampling).

        Args:
            n_suggestions (int): The number of parameter combinations to suggest.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a suggested
                                  parameter combination in its original scale.
        """
        try:
            # Ensure training data is updated if experimental data exists but tensors don't
            if (
                not hasattr(self, "train_X") or not hasattr(self, "train_Y")
            ) and not self.experimental_data.empty:
                logger.info("Updating training data tensors from experimental data")
                self._update_training_data()

            # Check if there's enough data to train the Gaussian Process models.
            if (
                not hasattr(self, "train_X")
                or not hasattr(self, "train_Y")
                or self.train_X.shape[0] < MIN_DATA_POINTS_FOR_GP
            ):
                logger.info("Insufficient data for GP. Using initial sampling method.")
                if self.initial_sampling_method == "LHS":
                    return self._generate_doe_samples(n_suggestions, method="LHS")
                else:
                    return self._generate_random_samples(n_suggestions)

            # Build the Gaussian Process models based on the current experimental data.
            models = self._build_models()
            if models is None:
                logger.warning("Could not build models. Using random sampling.")
                return self._generate_random_samples(n_suggestions)

            # Set up the acquisition function (e.g., Expected Hypervolume Improvement for MOO,
            # Expected Improvement for SOO).
            acq_func = self._setup_acquisition_function(models)
            if acq_func is None:
                logger.warning(
                    "Could not set up acquisition function. Using random sampling."
                )
                return self._generate_random_samples(n_suggestions)

            # Optimize the acquisition function to find the next best experimental points.
            suggestions = self._optimize_acquisition_function(acq_func, n_suggestions)

            logger.info(
                f"Generated {len(suggestions)} suggestions using Bayesian optimization"
            )
            return suggestions

        except Exception as e:
            logger.error(f"Error in suggest_next_experiment: {e}", exc_info=True)
            # Fallback to random sampling in case of any unexpected error.
            return self._generate_random_samples(n_suggestions)

    def _generate_random_samples(self, n_suggestions: int) -> List[Dict[str, Any]]:
        """
        Generates random samples in the parameter space. This is used as a fallback
        or for initial data generation when more sophisticated methods are not applicable.

        Args:
            n_suggestions (int): The number of random samples to generate.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a randomly
                                  generated parameter combination.
        """
        suggestions = []
        max_attempts = n_suggestions * 10  # Limit attempts to prevent infinite loops
        attempts = 0

        while len(suggestions) < n_suggestions and attempts < max_attempts:
            # Generate a random sample in the normalized [0, 1] space for each parameter.
            sample = torch.rand(
                len(self.parameter_transformer.param_names), dtype=self.dtype
            )
            # Convert the normalized sample back to the original parameter dictionary.
            param_dict = self.parameter_transformer.tensor_to_params(sample)

            # Check for uniqueness to avoid duplicate suggestions.
            is_unique = True
            for existing in suggestions:
                if self._are_params_similar(param_dict, existing):
                    is_unique = False
                    break

            if is_unique:
                suggestions.append(param_dict)

            attempts += 1

        logger.info(f"Generated {len(suggestions)} random suggestions.")
        return suggestions

    def _are_params_similar(
        self, params1: Dict[str, Any], params2: Dict[str, Any], rtol: float = 1e-3
    ) -> bool:
        """
        Compares two sets of parameters to determine if they are similar within a
        given relative tolerance. This is used to avoid suggesting duplicate experiments.

        Args:
            params1 (Dict[str, Any]): The first dictionary of parameters.
            params2 (Dict[str, Any]): The second dictionary of parameters.
            rtol (float): The relative tolerance for comparing numerical values.

        Returns:
            bool: True if the parameter sets are similar, False otherwise.
        """
        # Check if all keys in params1 are present in params2 and vice-versa
        if set(params1.keys()) != set(params2.keys()):
            return False

        for key in params1:
            val1, val2 = params1[key], params2[key]

            # Compare numerical values using numpy.isclose for tolerance.
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if not np.isclose(val1, val2, rtol=rtol):
                    return False
            # For non-numerical values, perform exact comparison.
            elif val1 != val2:
                return False

        return True

    def _build_models(self) -> Optional[ModelListGP]:
        """
        Builds and fits Gaussian Process (GP) models for each objective.
        A `SingleTaskGP` model is created for each objective, and then all
        models are combined into a `ModelListGP`.

        Returns:
            Optional[ModelListGP]: A `ModelListGP` containing the fitted GP models,
                                   or None if models cannot be built (e.g., insufficient data).
        """
        try:
            # Check if training data exists
            if not hasattr(self, "train_X") or not hasattr(self, "train_Y"):
                logger.warning("No training data available for model building.")
                return None

            if self.train_X.shape[0] == 0 or self.train_Y.shape[0] == 0:
                logger.warning("Empty training data for model building.")
                return None

            models = []

            for i, obj_name in enumerate(self.objective_names):
                if i >= self.train_Y.shape[1]:
                    logger.warning(
                        f"Objective index {i} exceeds training data dimensions for {obj_name}"
                    )
                    continue

                Y_obj = self.train_Y[:, i]

                # Filter out non-finite (NaN or Inf) values for the current objective.
                finite_mask = torch.isfinite(Y_obj)
                if finite_mask.sum() < MIN_DATA_POINTS_FOR_GP:
                    logger.warning(
                        f"Insufficient finite data points ({finite_mask.sum()}) for objective {obj_name}. Skipping model building for this objective."
                    )
                    continue

                X_filtered = self.train_X[finite_mask]
                Y_filtered = Y_obj[finite_mask].unsqueeze(
                    -1
                )  # Add a feature dimension for BoTorch.

                # Initialize a SingleTaskGP model.
                # - `MaternKernel` with nu=2.5 is a common choice for smooth functions.
                # - `ScaleKernel` scales the output of the Matern kernel.
                # - `Normalize` input transform normalizes input features to [0, 1].
                # - `Standardize` outcome transform standardizes output features to zero mean and unit variance.
                model = SingleTaskGP(
                    train_X=X_filtered,
                    train_Y=Y_filtered,
                    covar_module=ScaleKernel(
                        MaternKernel(nu=2.5, ard_num_dims=X_filtered.shape[-1])
                    ),
                    input_transform=Normalize(d=X_filtered.shape[-1]),
                    outcome_transform=Standardize(m=1),
                )

                # Fit the GP model by optimizing the marginal log-likelihood.
                mll = ExactMarginalLogLikelihood(model.likelihood, model)
                fit_gpytorch_mll(mll)

                models.append(model)

            if not models:
                logger.warning("No GP models could be built for any objective.")
                return None

            # Validate that we have models for all objectives
            if len(models) != len(self.objective_names):
                logger.error(f"Model count mismatch: built {len(models)} models for {len(self.objective_names)} objectives")
                logger.error(f"Objectives: {self.objective_names}")
                logger.error("This can cause dimension mismatches in acquisition functions")
                return None

            # Return a ModelListGP if multiple objectives, or the single model if only one.
            logger.debug(f"Successfully built {len(models)} models for objectives: {self.objective_names}")
            return ModelListGP(*models) if len(models) > 1 else models[0]

        except Exception as e:
            logger.error(f"Error building models: {e}", exc_info=True)
            return None

    def _setup_acquisition_function(
        self, models: Union[SingleTaskGP, ModelListGP]
    ) -> Optional[Union[LogExpectedImprovement, ExpectedHypervolumeImprovement]]:
        """
        Sets up the appropriate acquisition function based on the number of objectives.
        For multi-objective optimization, Expected Hypervolume Improvement (EHVI) is used.
        For single-objective optimization, Expected Improvement (EI) is used.

        Args:
            models (Union[SingleTaskGP, ModelListGP]): The fitted GP model(s).

        Returns:
            Optional[Union[LogExpectedImprovement, ExpectedHypervolumeImprovement]]:
                The initialized acquisition function, or None if setup fails.
        """
        try:
            if not hasattr(self, "train_Y") or self.train_Y.shape[0] == 0:
                logger.warning(
                    "No training data available to set up acquisition function."
                )
                return None

            if len(self.objective_names) > 1:
                # Multi-objective: use EHVI
                finite_mask = torch.isfinite(self.train_Y).all(dim=1)
                if not finite_mask.any():
                    logger.warning("No finite data points for EHVI calculation.")
                    return None
                clean_Y = self.train_Y[finite_mask]

                if clean_Y.shape[0] == 0:
                    logger.warning("No clean data points for EHVI calculation.")
                    return None

                # Use the same adaptive reference point calculation as in hypervolume calculation
                # This ensures consistency between hypervolume measurement and acquisition optimization
                ref_point = self._calculate_adaptive_reference_point(clean_Y)

                logger.debug(f"Ref point for HVI: {ref_point}")
                logger.debug(f"Clean Y shape: {clean_Y.shape}")
                logger.debug(f"Ref point shape: {ref_point.shape}")
                
                # Validate dimensions before creating acquisition function
                if ref_point.shape[0] != clean_Y.shape[1]:
                    logger.error(f"Dimension mismatch: ref_point has {ref_point.shape[0]} dimensions, "
                               f"but clean_Y has {clean_Y.shape[1]} objectives")
                    return None
                
                try:
                    partitioning = FastNondominatedPartitioning(
                        ref_point=ref_point, Y=clean_Y
                    )
                    
                    # Additional validation for model compatibility
                    if isinstance(models, ModelListGP):
                        expected_outputs = len(models.models)
                    else:
                        expected_outputs = models.num_outputs if hasattr(models, 'num_outputs') else 1
                    
                    if expected_outputs != clean_Y.shape[1]:
                        logger.error(f"Model outputs ({expected_outputs}) don't match data objectives ({clean_Y.shape[1]})")
                        return None
                    
                    ehvi = ExpectedHypervolumeImprovement(
                        model=models,
                        ref_point=ref_point.tolist(),
                        partitioning=partitioning,
                    )
                    
                    # Test the acquisition function with a dummy input to catch dimension issues early
                    try:
                        test_input = torch.randn(1, len(self.parameter_transformer.param_names), 
                                               dtype=self.dtype, device=self.device)
                        test_output = ehvi(test_input)
                        logger.debug(f"EHVI test successful: output shape {test_output.shape}")
                        return ehvi
                    except Exception as test_e:
                        logger.error(f"EHVI test failed with test input: {test_e}")
                        logger.error(f"Test input shape: {test_input.shape}")
                        logger.error(f"Expected parameters: {len(self.parameter_transformer.param_names)}")
                        
                        # Try fallback to simpler acquisition function for multi-objective
                        logger.warning("Attempting fallback to scalarized Expected Improvement")
                        try:
                            # Use a simple weighted scalarization as fallback
                            return self._create_scalarized_ei_fallback(models, clean_Y)
                        except Exception as fallback_e:
                            logger.error(f"Fallback acquisition function also failed: {fallback_e}")
                            return None
                except Exception as e:
                    logger.error(
                        f"Error creating EHVI acquisition function: {e}"
                    )
                    logger.error(f"Model type: {type(models)}")
                    logger.error(f"Clean Y shape: {clean_Y.shape}")
                    logger.error(f"Ref point: {ref_point}")
                    return None
            else:
                # Single objective: use EI
                finite_Y = self.train_Y[torch.isfinite(self.train_Y)]
                if finite_Y.numel() == 0:
                    logger.warning("No finite data points for EI calculation.")
                    return None

                # best_f is the maximum observed value in the transformed space
                # (which is correct for both maximization and minimization after negation)
                best_f = finite_Y.max()
                # If models is a SingleTaskGP, use it directly; otherwise, use models.models[0]
                if isinstance(models, SingleTaskGP):
                    return LogExpectedImprovement(model=models, best_f=best_f)
                else:
                    return LogExpectedImprovement(model=models.models[0], best_f=best_f)

        except Exception as e:
            logger.error(f"Error setting up acquisition function: {e}", exc_info=True)
            return None

    def _create_scalarized_ei_fallback(self, models, clean_Y):
        """
        Creates a fallback scalarized Expected Improvement acquisition function
        when EHVI fails due to dimension mismatches.
        
        Args:
            models: The GP models
            clean_Y: Clean training objectives
            
        Returns:
            A scalarized acquisition function or None if it fails
        """
        try:
            from botorch.acquisition.multi_objective import qExpectedImprovement
            from botorch.utils.multi_objective.scalarization import get_chebyshev_scalarization
            
            # Create equal weights for all objectives (could be made configurable)
            weights = torch.ones(clean_Y.shape[1], dtype=self.dtype, device=self.device) / clean_Y.shape[1]
            
            # Use Chebyshev scalarization
            transform = get_chebyshev_scalarization(weights=weights, Y=clean_Y)
            
            # Create scalarized EI
            scalarized_ei = qExpectedImprovement(
                model=models,
                objective=transform,
                best_f=transform(clean_Y).max(),
            )
            
            # Test the fallback acquisition function
            test_input = torch.randn(1, len(self.parameter_transformer.param_names), 
                                   dtype=self.dtype, device=self.device)
            test_output = scalarized_ei(test_input)
            logger.info(f"Scalarized EI fallback successful: output shape {test_output.shape}")
            
            return scalarized_ei
            
        except Exception as e:
            logger.error(f"Failed to create scalarized EI fallback: {e}")
            return None

    def _optimize_acquisition_function(
        self,
        acq_func: Union[LogExpectedImprovement, ExpectedHypervolumeImprovement],
        n_suggestions: int,
    ) -> List[Dict[str, Any]]:
        """
        Optimizes the acquisition function to find the next set of suggested experimental
        points. This involves using a multi-start optimization approach to find the
        global optimum of the acquisition function.

        Args:
            acq_func (Union[LogExpectedImprovement, ExpectedHypervolumeImprovement]): The
                       initialized acquisition function to be optimized.
            n_suggestions (int): The number of suggested points to generate.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a suggested
                                  parameter combination in its original scale.
        """
        try:
            # Define the bounds for the optimization of the acquisition function.
            # These are typically the normalized [0, 1] bounds of the parameter space.
            bounds = torch.stack(
                [
                    torch.zeros(
                        len(self.parameter_transformer.param_names), dtype=self.dtype
                    ),
                    torch.ones(
                        len(self.parameter_transformer.param_names), dtype=self.dtype
                    ),
                ]
            ).to(self.device)

            # Optimize the acquisition function using `optimize_acqf` from BoTorch.
            # `q` specifies the number of points to optimize for (batch size).
            # `num_restarts` and `raw_samples` control the multi-start optimization process.
            candidates, _ = optimize_acqf(
                acq_function=acq_func,
                bounds=bounds,
                q=n_suggestions,
                num_restarts=self.num_restarts,  # Number of restarts for optimization
                raw_samples=self.raw_samples,  # Number of raw samples for initialization
            )

            suggestions = []
            for i in range(candidates.shape[0]):
                # Convert the normalized candidate tensor back to a parameter dictionary.
                param_dict = self.parameter_transformer.tensor_to_params(candidates[i])
                suggestions.append(param_dict)

            logger.info(
                f"Successfully optimized acquisition function and generated {len(suggestions)} candidates."
            )
            return suggestions

        except Exception as e:
            logger.error(f"Error optimizing acquisition function: {e}", exc_info=True)
            # Fallback to random sampling in case of any unexpected error.
            return self._generate_random_samples(n_suggestions)

    def get_pareto_front(self) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
        """
        Identifies and returns the Pareto front from the observed experimental data.
        The Pareto front consists of non-dominated solutions, meaning no other solution
        is better in all objectives.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
                - A DataFrame of parameters corresponding to the Pareto front.
                - A DataFrame of objective values corresponding to the Pareto front.
                - A NumPy array of original indices of the Pareto optimal points in the
                  `experimental_data` DataFrame.
                Returns empty DataFrames and array if no data or no finite data points.
        """
        try:
            if (
                not hasattr(self, "train_Y")
                or not hasattr(self, "train_X")
                or self.train_Y.shape[0] == 0
            ):
                logger.debug("No training data available to determine Pareto front.")
                return pd.DataFrame(), pd.DataFrame(), np.array([])

            # Filter out rows containing NaN values in objectives.
            finite_mask = torch.isfinite(self.train_Y).all(dim=1)
            if not finite_mask.any():
                logger.debug("No finite data points to determine Pareto front.")
                return pd.DataFrame(), pd.DataFrame(), np.array([])

            clean_Y = self.train_Y[finite_mask]  # Filtered objective values
            clean_X = self.train_X[finite_mask]  # Filtered parameter values
            clean_indices = torch.where(finite_mask)[
                0
            ]  # Original indices of finite points

            # Use BoTorch's `is_non_dominated` to find Pareto optimal points.
            pareto_mask = is_non_dominated(clean_Y)
            pareto_Y = clean_Y[pareto_mask]  # Objective values on the Pareto front
            pareto_X = clean_X[pareto_mask]  # Parameter values on the Pareto front
            pareto_indices = clean_indices[
                pareto_mask
            ]  # Original indices of Pareto points

            # Convert objective values back to their original scale (undo negation for minimization).
            pareto_Y_original = pareto_Y.clone()
            for i, direction in enumerate(self.objective_directions):
                if (
                    direction == -1
                ):  # If objective was minimized, negate back to original scale.
                    pareto_Y_original[:, i] = -pareto_Y_original[:, i]

            # Create Pandas DataFrames for the Pareto front parameters and objectives.
            pareto_X_df = pd.DataFrame(
                pareto_X.cpu().numpy(), columns=self.parameter_transformer.param_names
            )

            pareto_obj_df = pd.DataFrame(
                pareto_Y_original.cpu().numpy(), columns=self.objective_names
            )

            logger.info(f"Found {len(pareto_X_df)} points on the Pareto front.")
            return pareto_X_df, pareto_obj_df, pareto_indices.cpu().numpy()

        except Exception as e:
            logger.error(f"Error getting Pareto front: {e}", exc_info=True)
            return pd.DataFrame(), pd.DataFrame(), np.array([])

    def get_best_compromise_solution(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Estimates the best optimal parameter combination and its predicted responses.
        This is achieved by generating the next suggested experiment (which is optimized
        by the acquisition function) and then predicting the responses for that point
        using the trained Gaussian Process models.

        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]:
                - A dictionary representing the best predicted parameter combination.
                - A dictionary representing the predicted responses (mean and 95% CI)
                  for the best parameter combination.
                Returns empty dictionaries if no suggestions can be generated or
                predictions fail.
        """
        try:
            # Get the next suggested experiment from the optimizer.
            # This point is already optimized to be "best" in terms of the acquisition function.
            suggestions = self.suggest_next_experiment(n_suggestions=1)

            if not suggestions:
                logger.warning("No suggestions generated for best compromise solution.")
                return {}, {}

            best_predicted_params = suggestions[0]

            # Predict the responses at this suggested parameter combination.
            predicted_responses = self.predict_responses_at(best_predicted_params)

            logger.info("Successfully estimated best compromise solution.")
            return best_predicted_params, predicted_responses

        except Exception as e:
            logger.error(
                f"Error estimating best compromise solution: {e}", exc_info=True
            )
            return {}, {}

    def predict_responses_at(
        self, param_dict: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """
        Predicts the mean and 95% confidence interval for each objective at a given
        parameter combination using the trained Gaussian Process models.

        Args:
            param_dict (Dict[str, Any]): A dictionary representing the parameter
                                         combination for which to make predictions.

        Returns:
            Dict[str, Dict[str, float]]: A dictionary where keys are objective names
                                        and values are dictionaries containing 'mean',
                                        'lower_ci', and 'upper_ci' for that objective.
                                        Returns an empty dictionary if models cannot be
                                        built or prediction fails.
        """
        try:
            # Build or retrieve the GP models.
            models = self._build_models()
            if not models:
                logger.warning("Cannot predict responses: No models available.")
                return {}

            # Convert the input parameter dictionary to a normalized tensor.
            param_tensor = self.parameter_transformer.params_to_tensor(param_dict)
            X_test = param_tensor.unsqueeze(0)  # Add a batch dimension for prediction.

            predictions = {}
            # Iterate through each objective to get its prediction.
            for i, obj_name in enumerate(self.objective_names):
                # Ensure there is a model for the current objective.
                if i < len(models.models):
                    model = models.models[i]
                    with torch.no_grad():  # Disable gradient calculations for inference.
                        posterior = model.posterior(X_test)
                        mean = posterior.mean.item()
                        std = posterior.variance.sqrt().item()

                        # Calculate 95% confidence interval using a Z-score of 1.96
                        # for a normal distribution.
                        z_score = 1.96
                        lower_ci = mean - z_score * std
                        upper_ci = mean + z_score * std

                        # Undo negation for minimization objectives to return values
                        # in their original scale.
                        if self.objective_directions[i] == -1:
                            mean = -mean
                            # Negate and swap CIs to maintain lower/upper order.
                            lower_ci, upper_ci = -upper_ci, -lower_ci

                        predictions[obj_name] = {
                            "mean": mean,
                            "lower_ci": lower_ci,
                            "upper_ci": upper_ci,
                        }

            logger.info(f"Successfully predicted responses for {param_dict}.")
            return predictions

        except Exception as e:
            logger.error(f"Error predicting responses: {e}", exc_info=True)
            return {}

    def get_response_models(self) -> Dict[str, SingleTaskGP]:
        """
        Builds and returns individual `SingleTaskGP` models for each response variable
        (objective or non-objective response) based on the current experimental data.
        These models can be used for plotting or further analysis of individual responses.

        Returns:
            Dict[str, SingleTaskGP]: A dictionary where keys are response names and values
                                    are the fitted `SingleTaskGP` models for those responses.
                                    Returns an empty dictionary if no models can be built.
        """
        try:
            models_dict = {}

            # Iterate through each defined response in the configuration.
            for response_name in self.responses_config.keys():
                # Ensure the response data exists in the experimental data.
                if response_name not in self.experimental_data.columns:
                    logger.debug(
                        f"Response '{response_name}' not found in experimental data. Skipping model building."
                    )
                    continue

                X_data = []  # List to store parameter tensors for this response
                Y_data = []  # List to store response values for this response

                for _, row in self.experimental_data.iterrows():
                    # Extract parameter values for the current row.
                    param_dict = {
                        param_name: row[param_name]
                        for param_name in self.parameter_transformer.param_names
                    }

                    if response_name in row:
                        response_value = row[response_name]
                        # Handle cases where the response might be a list (e.g., multiple replicates).
                        if isinstance(response_value, list) and len(response_value) > 0:
                            mean_value = np.mean(response_value)
                        else:
                            mean_value = float(response_value)

                        # Only include finite (non-NaN) response values for model training.
                        if not np.isnan(mean_value):
                            X_tensor = self.parameter_transformer.params_to_tensor(
                                param_dict
                            )
                            X_data.append(X_tensor)
                            Y_data.append(mean_value)

                # Build a GP model only if sufficient data points are available for this response.
                if len(Y_data) >= MIN_DATA_POINTS_FOR_GP:
                    X_tensor = torch.stack(X_data).to(self.device, self.dtype)
                    Y_tensor = torch.tensor(
                        Y_data, dtype=self.dtype, device=self.device
                    ).unsqueeze(
                        -1
                    )  # Add feature dimension.

                    # Initialize and fit a SingleTaskGP model for this response.
                    model = SingleTaskGP(
                        train_X=X_tensor,
                        train_Y=Y_tensor,
                        covar_module=ScaleKernel(
                            MaternKernel(nu=2.5, ard_num_dims=X_tensor.shape[-1])
                        ),
                        input_transform=Normalize(d=X_tensor.shape[-1]),
                        outcome_transform=Standardize(m=1),
                    )

                    mll = ExactMarginalLogLikelihood(model.likelihood, model)
                    fit_gpytorch_mll(mll)

                    models_dict[response_name] = model
                    logger.debug(
                        f"Successfully built GP model for response: {response_name}"
                    )
                else:
                    logger.warning(
                        f"Insufficient data points ({len(Y_data)}) for response '{response_name}'. Skipping model building."
                    )

            return models_dict

        except Exception as e:
            logger.error(f"Error building response models: {e}", exc_info=True)
            return {}

    def get_predicted_values(self, response_name: str) -> np.ndarray:
        """
        Returns the predicted mean values for a given response based on the current
        experimental data and the fitted Gaussian Process model for that response.

        Args:
            response_name (str): The name of the response variable for which to get
                                 predicted values.

        Returns:
            np.ndarray: A NumPy array containing the predicted mean values for the
                        specified response at the observed experimental points.
                        Returns an empty array if no model is available or prediction fails.
        """
        try:
            models = self.get_response_models()
            model = models.get(response_name)

            if (
                model is None
                or not hasattr(self, "train_X")
                or self.train_X.shape[0] == 0
            ):
                logger.warning(
                    f"Cannot get predicted values for {response_name}: No model or training data available."
                )
                return np.array([])

            with torch.no_grad():
                # Predict the mean of the posterior distribution at the training points.
                posterior = model.posterior(model.train_inputs[0])
                mean = posterior.mean.squeeze().cpu().numpy()

                # Undo negation if the objective was minimized to return original scale.
                if response_name in self.objective_names:
                    obj_idx = self.objective_names.index(response_name)
                    if self.objective_directions[obj_idx] == -1:
                        mean = -mean

            logger.debug(
                f"Successfully retrieved predicted values for {response_name}."
            )
            return mean
        except Exception as e:
            logger.error(
                f"Error getting predicted values for {response_name}: {e}",
                exc_info=True,
            )
            return np.array([])

    def get_feature_importances(self, response_name: str) -> Dict[str, float]:
        """
        Extracts feature importances (inverse lengthscales) from the GP model for a given response.
        """
        try:
            models = self.get_response_models()
            model = models.get(response_name)

            if (
                model is None
                or not hasattr(model.covar_module, "base_kernel")
                or not hasattr(model.covar_module.base_kernel, "lengthscale")
            ):
                logger.warning(
                    f"Model for {response_name} does not have lengthscales for sensitivity analysis."
                )
                return {}

            # Lengthscales are typically inverse to importance: smaller lengthscale means more important feature
            # We take the inverse to represent importance
            lengthscales = (
                model.covar_module.base_kernel.lengthscale.squeeze()
                .detach()
                .cpu()
                .numpy()
            )

            # Handle input transforms if present
            if hasattr(model, "input_transform") and model.input_transform is not None:
                # If input is normalized, lengthscales are in normalized space.
                # For sensitivity, we care about relative importance, so direct inverse is usually fine.
                # If parameters have different scales, this might need more
                # sophisticated handling.
                pass

            importances = 1.0 / lengthscales

            # Normalize importances to sum to 1 for better interpretability
            total_importance = np.sum(importances)
            if total_importance > 0:
                importances = importances / total_importance

            feature_importances = {}
            for i, param_name in enumerate(self.parameter_transformer.param_names):
                feature_importances[param_name] = float(importances[i])  # Ensure JSON serializable

            return feature_importances
        except Exception as e:
            logger.error(f"Error getting feature importances for {response_name}: {e}")
            return {}
    
    def _validate_params_config(self, params_config: Dict[str, Dict[str, Any]]) -> None:
        """Validate parameter configuration for correctness and completeness.
        
        Args:
            params_config: Parameter configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(params_config, dict) or not params_config:
            raise ValueError("params_config must be a non-empty dictionary")
            
        for param_name, config in params_config.items():
            if not isinstance(config, dict):
                raise ValueError(f"Parameter '{param_name}' config must be a dictionary")
                
            # Check required fields
            if 'type' not in config:
                raise ValueError(f"Parameter '{param_name}' missing required 'type' field")
                
            param_type = config['type']
            if param_type not in ['continuous', 'categorical']:
                raise ValueError(f"Parameter '{param_name}' type must be 'continuous' or 'categorical'")
                
            if 'bounds' not in config:
                raise ValueError(f"Parameter '{param_name}' missing required 'bounds' field")
                
            bounds = config['bounds']
            if param_type == 'continuous':
                if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
                    raise ValueError(f"Continuous parameter '{param_name}' bounds must be [min, max]")
                if not all(isinstance(b, (int, float)) for b in bounds):
                    raise ValueError(f"Continuous parameter '{param_name}' bounds must be numeric")
                if bounds[0] >= bounds[1]:
                    raise ValueError(f"Continuous parameter '{param_name}' min bound must be < max bound")
            elif param_type == 'categorical':
                if not isinstance(bounds, (list, tuple)) or len(bounds) < 2:
                    raise ValueError(f"Categorical parameter '{param_name}' must have at least 2 values")
                    
        logger.debug(f"Parameter configuration validated: {len(params_config)} parameters")
    
    def _validate_responses_config(self, responses_config: Dict[str, Dict[str, Any]]) -> None:
        """Validate response configuration for correctness and completeness.
        
        Args:
            responses_config: Response configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(responses_config, dict) or not responses_config:
            raise ValueError("responses_config must be a non-empty dictionary")
            
        valid_goals = ['Maximize', 'Minimize', 'Target']
        
        for response_name, config in responses_config.items():
            if not isinstance(config, dict):
                raise ValueError(f"Response '{response_name}' config must be a dictionary")
                
            # Check goal field
            if 'goal' not in config:
                raise ValueError(f"Response '{response_name}' missing required 'goal' field")
                
            goal = config['goal']
            if goal not in valid_goals:
                raise ValueError(f"Response '{response_name}' goal must be one of {valid_goals}")
                
            # If goal is Target, check for target value
            if goal == 'Target' and 'target' not in config:
                raise ValueError(f"Response '{response_name}' with Target goal missing 'target' value")
                
        logger.debug(f"Response configuration validated: {len(responses_config)} responses")
