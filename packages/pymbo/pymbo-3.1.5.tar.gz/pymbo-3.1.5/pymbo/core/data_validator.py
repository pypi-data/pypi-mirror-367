"""
Data Validator - Specialized Data Validation and Transformation Module

This module provides comprehensive data validation, cleaning, and transformation
utilities for multi-objective Bayesian optimization. It handles parameter
validation, constraint checking, data type conversion, and outlier detection
with high performance and reliability.

Key Features:
- Fast parameter bounds validation
- Constraint expression safety checking
- Automatic data type conversion and cleaning
- Outlier detection and handling
- Missing value imputation strategies
- Thread-safe validation operations
- Batch validation for large datasets

Classes:
    DataValidator: Main data validation engine
    ConstraintValidator: Specialized constraint validation
    DataTransformer: Data transformation utilities
"""

import ast
import logging
import operator as op
import re
import threading
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import torch

logger = logging.getLogger(__name__)

# Security: Allowed operators for safe constraint expression evaluation
ALLOWED_CONSTRAINT_OPERATORS = {"+", "-", "*", "/", "(", ")", "<", ">", "=", " "}
ALLOWED_CONSTRAINT_FUNCTIONS = {"abs", "sqrt", "log", "exp", "sin", "cos", "tan", "min", "max"}

# Data validation constants
DEFAULT_OUTLIER_THRESHOLD = 3.0  # Standard deviations
MIN_VALID_DATA_RATIO = 0.1  # Minimum ratio of valid data points


class ConstraintValidator:
    """
    Specialized validator for optimization constraints.
    """
    
    def __init__(self):
        """Initialize constraint validator."""
        self._compiled_constraints = {}
        self._lock = threading.Lock()
    
    def validate_constraint_expression(self, constraint: str, param_names: List[str]) -> bool:
        """
        Validates a constraint expression for security and correctness.

        Args:
            constraint: The constraint expression to validate
            param_names: List of valid parameter names

        Returns:
            bool: True if constraint is safe, False otherwise
        """
        try:
            if not isinstance(constraint, str):
                return False

            # Remove whitespace for easier processing
            clean_constraint = constraint.replace(" ", "")

            # Check for dangerous patterns
            dangerous_patterns = [
                "import", "exec", "eval", "__", "getattr", "setattr", "delattr",
                "open", "file", "input", "raw_input", "compile", "globals", "locals"
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

        except Exception as e:
            logger.error(f"Error validating constraint: {e}")
            return False
    
    def compile_constraint(self, constraint: str, param_names: List[str]) -> Optional[Any]:
        """
        Compile constraint expression for efficient evaluation.
        
        Args:
            constraint: Constraint expression string
            param_names: List of parameter names
            
        Returns:
            Compiled constraint or None if compilation fails
        """
        try:
            if not self.validate_constraint_expression(constraint, param_names):
                return None
            
            cache_key = f"{constraint}_{hash(tuple(param_names))}"
            
            with self._lock:
                if cache_key in self._compiled_constraints:
                    return self._compiled_constraints[cache_key]
            
            # Compile the constraint
            compiled_expr = compile(constraint, '<constraint>', 'eval')
            
            with self._lock:
                self._compiled_constraints[cache_key] = compiled_expr
            
            return compiled_expr
            
        except Exception as e:
            logger.error(f"Error compiling constraint '{constraint}': {e}")
            return None
    
    def evaluate_constraint(
        self, 
        compiled_constraint: Any, 
        param_dict: Dict[str, float]
    ) -> bool:
        """
        Safely evaluate a compiled constraint.
        
        Args:
            compiled_constraint: Compiled constraint expression
            param_dict: Dictionary of parameter values
            
        Returns:
            bool: True if constraint is satisfied, False otherwise
        """
        try:
            # Create safe evaluation environment
            safe_dict = {
                "__builtins__": {},
                "abs": abs, "min": min, "max": max,
                "sqrt": np.sqrt, "log": np.log, "exp": np.exp,
                "sin": np.sin, "cos": np.cos, "tan": np.tan
            }
            safe_dict.update(param_dict)
            
            result = eval(compiled_constraint, safe_dict)
            return bool(result)
            
        except Exception as e:
            logger.warning(f"Error evaluating constraint: {e}")
            return False


class DataTransformer:
    """
    Utilities for data transformation and preprocessing.
    """
    
    def __init__(self):
        """Initialize data transformer."""
        pass
    
    def normalize_data(self, data: np.ndarray, bounds: np.ndarray) -> np.ndarray:
        """
        Normalize data to [0, 1] range based on provided bounds.
        
        Args:
            data: Input data array [n_samples, n_features]
            bounds: Bounds array [n_features, 2] with [min, max] for each feature
            
        Returns:
            Normalized data array
        """
        try:
            normalized = np.zeros_like(data)
            
            for i in range(data.shape[1]):
                min_val, max_val = bounds[i]
                if max_val > min_val:
                    normalized[:, i] = (data[:, i] - min_val) / (max_val - min_val)
                else:
                    normalized[:, i] = 0.5  # Default to middle if bounds are invalid
            
            return np.clip(normalized, 0, 1)
            
        except Exception as e:
            logger.error(f"Error normalizing data: {e}")
            return data
    
    def denormalize_data(self, data: np.ndarray, bounds: np.ndarray) -> np.ndarray:
        """
        Denormalize data from [0, 1] range back to original bounds.
        
        Args:
            data: Normalized data array [n_samples, n_features]
            bounds: Bounds array [n_features, 2] with [min, max] for each feature
            
        Returns:
            Denormalized data array
        """
        try:
            denormalized = np.zeros_like(data)
            
            for i in range(data.shape[1]):
                min_val, max_val = bounds[i]
                denormalized[:, i] = data[:, i] * (max_val - min_val) + min_val
            
            return denormalized
            
        except Exception as e:
            logger.error(f"Error denormalizing data: {e}")
            return data
    
    def impute_missing_values(
        self, 
        data: pd.DataFrame, 
        strategy: str = "mean"
    ) -> pd.DataFrame:
        """
        Impute missing values in dataset.
        
        Args:
            data: Input DataFrame with potential missing values
            strategy: Imputation strategy ("mean", "median", "mode", "forward_fill")
            
        Returns:
            DataFrame with imputed values
        """
        try:
            result = data.copy()
            
            for column in result.columns:
                if result[column].isnull().any():
                    if strategy == "mean":
                        fill_value = result[column].mean()
                    elif strategy == "median":
                        fill_value = result[column].median()
                    elif strategy == "mode":
                        fill_value = result[column].mode().iloc[0] if not result[column].mode().empty else 0
                    elif strategy == "forward_fill":
                        result[column] = result[column].fillna(method='ffill')
                        continue
                    else:
                        fill_value = 0
                    
                    result[column] = result[column].fillna(fill_value)
            
            return result
            
        except Exception as e:
            logger.error(f"Error imputing missing values: {e}")
            return data


class DataValidator:
    """
    Comprehensive data validation system for Bayesian optimization.
    
    This class provides fast, reliable validation of experimental data,
    parameter configurations, and optimization constraints.
    """
    
    def __init__(self):
        """Initialize data validator."""
        self.constraint_validator = ConstraintValidator()
        self.data_transformer = DataTransformer()
        self._validation_cache = {}
        self._lock = threading.Lock()
        
        logger.info("DataValidator initialized")
    
    def validate_params_config(self, params_config: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate parameter configuration for correctness and completeness.
        
        Args:
            params_config: Parameter configuration dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            if not isinstance(params_config, dict) or not params_config:
                errors.append("params_config must be a non-empty dictionary")
                return False, errors
                
            for param_name, config in params_config.items():
                if not isinstance(config, dict):
                    errors.append(f"Parameter '{param_name}' config must be a dictionary")
                    continue
                    
                # Check required fields
                if 'type' not in config:
                    errors.append(f"Parameter '{param_name}' missing required 'type' field")
                    continue
                    
                param_type = config['type']
                if param_type not in ['continuous', 'discrete', 'categorical']:
                    errors.append(f"Parameter '{param_name}' type must be 'continuous', 'discrete', or 'categorical'")
                    continue
                    
                # Validate bounds/values based on type
                if param_type in ['continuous', 'discrete']:
                    if 'bounds' not in config:
                        errors.append(f"Parameter '{param_name}' missing required 'bounds' field")
                        continue
                        
                    bounds = config['bounds']
                    if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
                        errors.append(f"Parameter '{param_name}' bounds must be [min, max]")
                        continue
                        
                    if not all(isinstance(b, (int, float)) for b in bounds):
                        errors.append(f"Parameter '{param_name}' bounds must be numeric")
                        continue
                        
                    if bounds[0] >= bounds[1]:
                        errors.append(f"Parameter '{param_name}' min bound must be < max bound")
                        
                elif param_type == 'categorical':
                    if 'values' not in config:
                        errors.append(f"Categorical parameter '{param_name}' missing 'values' field")
                        continue
                        
                    values = config['values']
                    if not isinstance(values, (list, tuple)) or len(values) < 2:
                        errors.append(f"Categorical parameter '{param_name}' must have at least 2 values")
            
            is_valid = len(errors) == 0
            if is_valid:
                logger.debug(f"Parameter configuration validated: {len(params_config)} parameters")
            
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"Error validating params config: {e}")
            return False, [f"Validation error: {str(e)}"]
    
    def validate_responses_config(self, responses_config: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate response configuration for correctness and completeness.
        
        Args:
            responses_config: Response configuration dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            if not isinstance(responses_config, dict) or not responses_config:
                errors.append("responses_config must be a non-empty dictionary")
                return False, errors
                
            valid_goals = ['Maximize', 'Minimize', 'Target', 'None']
            
            for response_name, config in responses_config.items():
                if not isinstance(config, dict):
                    errors.append(f"Response '{response_name}' config must be a dictionary")
                    continue
                    
                # Check goal field
                if 'goal' not in config:
                    errors.append(f"Response '{response_name}' missing required 'goal' field")
                    continue
                    
                goal = config['goal']
                if goal not in valid_goals:
                    errors.append(f"Response '{response_name}' goal must be one of {valid_goals}")
                    continue
                    
                # If goal is Target, check for target value
                if goal == 'Target' and 'target' not in config:
                    errors.append(f"Response '{response_name}' with Target goal missing 'target' value")
            
            is_valid = len(errors) == 0
            if is_valid:
                logger.debug(f"Response configuration validated: {len(responses_config)} responses")
            
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"Error validating responses config: {e}")
            return False, [f"Validation error: {str(e)}"]
    
    def validate_experimental_data(
        self,
        data_df: pd.DataFrame,
        params_config: Dict[str, Dict[str, Any]],
        responses_config: Dict[str, Dict[str, Any]] = None,
        check_outliers: bool = True,
        outlier_threshold: float = DEFAULT_OUTLIER_THRESHOLD
    ) -> Dict[str, Any]:
        """
        Comprehensive validation of experimental data.
        
        Args:
            data_df: Experimental data DataFrame
            params_config: Parameter configuration
            responses_config: Response configuration (optional)
            check_outliers: Whether to perform outlier detection
            outlier_threshold: Threshold for outlier detection (standard deviations)
            
        Returns:
            Dictionary with validation results and statistics
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {},
            "cleaned_data": data_df.copy()
        }
        
        try:
            # Check if DataFrame is empty
            if data_df.empty:
                result["errors"].append("Data DataFrame is empty")
                result["is_valid"] = False
                return result
            
            # Validate parameter columns
            param_names = list(params_config.keys())
            missing_params = [p for p in param_names if p not in data_df.columns]
            if missing_params:
                result["errors"].append(f"Missing parameter columns: {missing_params}")
                result["is_valid"] = False
            
            # Validate parameter values and bounds
            for param_name, config in params_config.items():
                if param_name not in data_df.columns:
                    continue
                
                param_data = data_df[param_name]
                param_type = config.get('type', 'continuous')
                
                # Check for missing values
                missing_count = param_data.isnull().sum()
                if missing_count > 0:
                    result["warnings"].append(f"Parameter '{param_name}' has {missing_count} missing values")
                
                # Type-specific validation
                if param_type in ['continuous', 'discrete']:
                    # Check if values are numeric
                    try:
                        numeric_data = pd.to_numeric(param_data, errors='coerce')
                        non_numeric_count = numeric_data.isnull().sum() - missing_count
                        if non_numeric_count > 0:
                            result["warnings"].append(f"Parameter '{param_name}' has {non_numeric_count} non-numeric values")
                        
                        # Check bounds
                        if 'bounds' in config:
                            min_val, max_val = config['bounds']
                            valid_data = numeric_data.dropna()
                            if not valid_data.empty:
                                out_of_bounds = ((valid_data < min_val) | (valid_data > max_val)).sum()
                                if out_of_bounds > 0:
                                    result["warnings"].append(f"Parameter '{param_name}' has {out_of_bounds} values outside bounds [{min_val}, {max_val}]")
                        
                    except Exception as e:
                        result["warnings"].append(f"Error validating parameter '{param_name}': {e}")
                
                elif param_type == 'categorical':
                    if 'values' in config:
                        valid_values = set(config['values'])
                        invalid_values = set(param_data.dropna()) - valid_values
                        if invalid_values:
                            result["warnings"].append(f"Parameter '{param_name}' has invalid values: {invalid_values}")
            
            # Validate response columns if provided
            if responses_config:
                response_names = list(responses_config.keys())
                available_responses = [r for r in response_names if r in data_df.columns]
                
                if not available_responses:
                    result["warnings"].append("No response columns found in data")
                
                for response_name in available_responses:
                    response_data = data_df[response_name]
                    
                    # Check for missing values
                    missing_count = response_data.isnull().sum()
                    if missing_count > 0:
                        result["warnings"].append(f"Response '{response_name}' has {missing_count} missing values")
                    
                    # Check if values are numeric
                    try:
                        numeric_data = pd.to_numeric(response_data, errors='coerce')
                        non_numeric_count = numeric_data.isnull().sum() - missing_count
                        if non_numeric_count > 0:
                            result["warnings"].append(f"Response '{response_name}' has {non_numeric_count} non-numeric values")
                    except Exception:
                        result["warnings"].append(f"Error validating response '{response_name}'")
            
            # Outlier detection
            if check_outliers:
                outlier_stats = self._detect_outliers(data_df, param_names, outlier_threshold)
                result["statistics"]["outliers"] = outlier_stats
                
                total_outliers = sum(outlier_stats.values())
                if total_outliers > 0:
                    result["warnings"].append(f"Detected {total_outliers} potential outliers")
            
            # Calculate basic statistics
            result["statistics"]["basic"] = self._calculate_basic_statistics(data_df, param_names)
            
            # Data quality score
            quality_score = self._calculate_quality_score(result)
            result["statistics"]["quality_score"] = quality_score
            
            logger.debug(f"Data validation completed. Quality score: {quality_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in data validation: {e}")
            result["errors"].append(f"Validation error: {str(e)}")
            result["is_valid"] = False
            return result
    
    def clean_experimental_data(
        self,
        data_df: pd.DataFrame,
        params_config: Dict[str, Dict[str, Any]],
        remove_outliers: bool = False,
        outlier_threshold: float = DEFAULT_OUTLIER_THRESHOLD,
        impute_missing: bool = True,
        imputation_strategy: str = "mean"
    ) -> pd.DataFrame:
        """
        Clean experimental data by handling missing values and outliers.
        
        Args:
            data_df: Input data DataFrame
            params_config: Parameter configuration
            remove_outliers: Whether to remove outlier rows
            outlier_threshold: Threshold for outlier detection
            impute_missing: Whether to impute missing values
            imputation_strategy: Strategy for imputing missing values
            
        Returns:
            Cleaned DataFrame
        """
        try:
            cleaned_data = data_df.copy()
            
            # Handle missing values
            if impute_missing:
                cleaned_data = self.data_transformer.impute_missing_values(cleaned_data, imputation_strategy)
            
            # Remove outliers if requested
            if remove_outliers:
                param_names = list(params_config.keys())
                outlier_mask = self._get_outlier_mask(cleaned_data, param_names, outlier_threshold)
                cleaned_data = cleaned_data[~outlier_mask]
                logger.info(f"Removed {outlier_mask.sum()} outlier rows")
            
            # Ensure data types are correct
            for param_name, config in params_config.items():
                if param_name in cleaned_data.columns:
                    param_type = config.get('type', 'continuous')
                    
                    if param_type in ['continuous', 'discrete']:
                        cleaned_data[param_name] = pd.to_numeric(cleaned_data[param_name], errors='coerce')
                        
                        if param_type == 'discrete':
                            cleaned_data[param_name] = cleaned_data[param_name].round().astype('Int64')
            
            logger.info(f"Data cleaning completed. Shape: {cleaned_data.shape}")
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            return data_df
    
    def _detect_outliers(
        self, 
        data_df: pd.DataFrame, 
        param_names: List[str], 
        threshold: float
    ) -> Dict[str, int]:
        """Detect outliers using z-score method."""
        outlier_counts = {}
        
        try:
            for param_name in param_names:
                if param_name in data_df.columns:
                    param_data = pd.to_numeric(data_df[param_name], errors='coerce').dropna()
                    
                    if len(param_data) > 0:
                        z_scores = np.abs((param_data - param_data.mean()) / param_data.std())
                        outliers = (z_scores > threshold).sum()
                        outlier_counts[param_name] = int(outliers)
                    else:
                        outlier_counts[param_name] = 0
            
            return outlier_counts
            
        except Exception as e:
            logger.error(f"Error detecting outliers: {e}")
            return {}
    
    def _get_outlier_mask(
        self, 
        data_df: pd.DataFrame, 
        param_names: List[str], 
        threshold: float
    ) -> pd.Series:
        """Get boolean mask for outlier rows."""
        try:
            outlier_mask = pd.Series(False, index=data_df.index)
            
            for param_name in param_names:
                if param_name in data_df.columns:
                    param_data = pd.to_numeric(data_df[param_name], errors='coerce')
                    valid_data = param_data.dropna()
                    
                    if len(valid_data) > 0:
                        z_scores = np.abs((param_data - valid_data.mean()) / valid_data.std())
                        outlier_mask |= (z_scores > threshold)
            
            return outlier_mask
            
        except Exception as e:
            logger.error(f"Error creating outlier mask: {e}")
            return pd.Series(False, index=data_df.index)
    
    def _calculate_basic_statistics(
        self, 
        data_df: pd.DataFrame, 
        param_names: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate basic statistics for parameters."""
        stats = {}
        
        try:
            for param_name in param_names:
                if param_name in data_df.columns:
                    param_data = pd.to_numeric(data_df[param_name], errors='coerce').dropna()
                    
                    if len(param_data) > 0:
                        stats[param_name] = {
                            "mean": float(param_data.mean()),
                            "std": float(param_data.std()),
                            "min": float(param_data.min()),
                            "max": float(param_data.max()),
                            "count": int(len(param_data))
                        }
                    else:
                        stats[param_name] = {
                            "mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "count": 0
                        }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def _calculate_quality_score(self, validation_result: Dict[str, Any]) -> float:
        """Calculate overall data quality score (0-1)."""
        try:
            score = 1.0
            
            # Penalize for errors
            num_errors = len(validation_result.get("errors", []))
            score -= num_errors * 0.2
            
            # Penalize for warnings
            num_warnings = len(validation_result.get("warnings", []))
            score -= num_warnings * 0.05
            
            # Bonus for completeness
            stats = validation_result.get("statistics", {})
            if "basic" in stats:
                total_data_points = sum(s.get("count", 0) for s in stats["basic"].values())
                if total_data_points > 100:
                    score += 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5  # Default neutral score