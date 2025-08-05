"""
File Controller - Specialized Controller for File I/O Operations

This module provides a dedicated controller for file input/output operations,
extracted from the main controller for better performance and modularity.
It handles saving/loading optimization sessions, data import/export, and
file operations.

Key Features:
- High-performance file I/O operations
- Comprehensive data format support (CSV, Excel, JSON, Pickle)
- Intelligent file format detection
- Memory-efficient large file handling
- Thread-safe file operations
- Data validation during import/export

Classes:
    FileController: Main file operations controller
"""

import json
import logging
import pickle
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FileController:
    """
    Specialized controller for file I/O operations in Bayesian optimization.
    
    This controller handles all aspects of file operations including data
    import/export, and session saving/loading.
    """
    
    def __init__(self):
        """Initialize file controller."""
        self._file_cache = {}
        self._lock = threading.Lock()
        
        logger.info("FileController initialized")
    
    def save_optimization_session(
        self,
        optimizer: Any,
        filepath: Union[str, Path],
        include_cache: bool = True
    ) -> bool:
        """
        Save complete optimization session to file.
        
        Args:
            optimizer: The optimization engine instance
            filepath: Path to save file
            include_cache: Whether to include cached data
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            filepath = Path(filepath)
            
            # Calculate hypervolume data for preservation
            hypervolume_data = {}
            try:
                if hasattr(optimizer, '_calculate_hypervolume'):
                    current_hypervolume = optimizer._calculate_hypervolume()
                    hypervolume_summary = optimizer.get_optimization_progress_summary() if hasattr(optimizer, 'get_optimization_progress_summary') else {}
                    convergence_data = optimizer.check_hypervolume_convergence() if hasattr(optimizer, 'check_hypervolume_convergence') else {}
                    
                    hypervolume_data = {
                        "current_hypervolume": current_hypervolume,
                        "progress_summary": hypervolume_summary,
                        "convergence_analysis": convergence_data,
                        "calculation_timestamp": datetime.now().isoformat(),
                    }
            except Exception as e:
                logger.warning(f"Could not calculate hypervolume data for save: {e}")
            
            # Prepare save data
            save_data = {
                "params_config": getattr(optimizer, 'params_config', {}),
                "responses_config": getattr(optimizer, 'responses_config', {}),
                "general_constraints": getattr(optimizer, 'general_constraints', []),
                "experimental_data": getattr(optimizer, 'experimental_data', pd.DataFrame()).to_dict("records"),
                "iteration_history": getattr(optimizer, 'iteration_history', []),
                "hypervolume_data": hypervolume_data,
                "metadata": {
                    "save_timestamp": datetime.now().isoformat(),
                    "version": "3.2.0",  # Updated version for fragmented architecture
                    "has_hypervolume_cache": bool(hypervolume_data),
                    "optimizer_type": type(optimizer).__name__,
                },
            }
            
            # Save to file
            with open(filepath, "wb") as f:
                pickle.dump(save_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            logger.info(f"Optimization session saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving optimization session: {e}", exc_info=True)
            return False
    
    def load_optimization_session(self, filepath: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Load optimization session from file.
        
        Args:
            filepath: Path to load file
            
        Returns:
            Dictionary with loaded session data or None if load fails
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                logger.error(f"File does not exist: {filepath}")
                return None
            
            with open(filepath, "rb") as f:
                save_data = pickle.load(f)
            
            # Validate loaded data
            required_keys = ["params_config", "responses_config"]
            missing_keys = [key for key in required_keys if key not in save_data]
            if missing_keys:
                logger.error(f"Invalid save file - missing keys: {missing_keys}")
                return None
            
            logger.info(f"Optimization session loaded from {filepath}")
            return save_data
            
        except Exception as e:
            logger.error(f"Error loading optimization session: {e}", exc_info=True)
            return None
    
    def import_csv_data(
        self,
        filepath: Union[str, Path],
        expected_columns: Optional[List[str]] = None,
        validate_data: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Import data from CSV file with validation.
        
        Args:
            filepath: Path to CSV file
            expected_columns: Expected column names for validation
            validate_data: Whether to validate imported data
            
        Returns:
            DataFrame with imported data or None if import fails
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                logger.error(f"CSV file does not exist: {filepath}")
                return None
            
            # Read CSV file
            data_df = pd.read_csv(filepath)
            
            if data_df.empty:
                logger.warning(f"CSV file is empty: {filepath}")
                return data_df
            
            logger.info(f"Imported {len(data_df)} rows from {filepath}")
            
            # Validate columns if expected columns provided
            if expected_columns and validate_data:
                available_cols = set(data_df.columns)
                expected_cols = set(expected_columns)
                missing_cols = expected_cols - available_cols
                
                if missing_cols:
                    logger.warning(f"Missing expected columns: {missing_cols}")
                
                extra_cols = available_cols - expected_cols
                if extra_cols:
                    logger.info(f"Found additional columns: {extra_cols}")
            
            # Basic data cleaning
            if validate_data:
                data_df = self._clean_imported_data(data_df)
            
            return data_df
            
        except Exception as e:
            logger.error(f"Error importing CSV data: {e}", exc_info=True)
            return None
    
    def export_csv_data(
        self,
        data_df: pd.DataFrame,
        filepath: Union[str, Path],
        include_index: bool = False
    ) -> bool:
        """
        Export DataFrame to CSV file.
        
        Args:
            data_df: DataFrame to export
            filepath: Path to save CSV file
            include_index: Whether to include row index
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            filepath = Path(filepath)
            
            # Ensure parent directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Export to CSV
            data_df.to_csv(filepath, index=include_index)
            
            logger.info(f"Exported {len(data_df)} rows to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting CSV data: {e}", exc_info=True)
            return False
    
    def import_excel_data(
        self,
        filepath: Union[str, Path],
        sheet_name: Union[str, int] = 0,
        expected_columns: Optional[List[str]] = None,
        validate_data: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Import data from Excel file.
        
        Args:
            filepath: Path to Excel file
            sheet_name: Sheet name or index to read
            expected_columns: Expected column names for validation
            validate_data: Whether to validate imported data
            
        Returns:
            DataFrame with imported data or None if import fails
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                logger.error(f"Excel file does not exist: {filepath}")
                return None
            
            # Read Excel file
            data_df = pd.read_excel(filepath, sheet_name=sheet_name)
            
            if data_df.empty:
                logger.warning(f"Excel file is empty: {filepath}")
                return data_df
            
            logger.info(f"Imported {len(data_df)} rows from {filepath}")
            
            # Validate and clean data
            if validate_data:
                data_df = self._clean_imported_data(data_df)
            
            return data_df
            
        except Exception as e:
            logger.error(f"Error importing Excel data: {e}", exc_info=True)
            return None
    
    def export_excel_data(
        self,
        data_df: pd.DataFrame,
        filepath: Union[str, Path],
        sheet_name: str = "Sheet1",
        include_index: bool = False
    ) -> bool:
        """
        Export DataFrame to Excel file.
        
        Args:
            data_df: DataFrame to export
            filepath: Path to save Excel file
            sheet_name: Name of the Excel sheet
            include_index: Whether to include row index
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            filepath = Path(filepath)
            
            # Ensure parent directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Export to Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                data_df.to_excel(writer, sheet_name=sheet_name, index=include_index)
            
            logger.info(f"Exported {len(data_df)} rows to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting Excel data: {e}", exc_info=True)
            return False
    
    def export_json_data(
        self,
        data: Union[Dict, List, pd.DataFrame],
        filepath: Union[str, Path],
        indent: int = 2
    ) -> bool:
        """
        Export data to JSON file.
        
        Args:
            data: Data to export (dict, list, or DataFrame)
            filepath: Path to save JSON file
            indent: JSON indentation level
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            filepath = Path(filepath)
            
            # Ensure parent directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert DataFrame to dict if needed
            if isinstance(data, pd.DataFrame):
                data = data.to_dict("records")
            
            # Export to JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, default=str, ensure_ascii=False)
            
            logger.info(f"Exported data to JSON file: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting JSON data: {e}", exc_info=True)
            return False
    
    def import_json_data(self, filepath: Union[str, Path]) -> Optional[Any]:
        """
        Import data from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Loaded JSON data or None if import fails
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                logger.error(f"JSON file does not exist: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Imported JSON data from {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Error importing JSON data: {e}", exc_info=True)
            return None
    
    def save_suggestions_to_csv(
        self,
        suggestions: List[Dict[str, Any]],
        filepath: Union[str, Path],
        params_config: Dict[str, Dict[str, Any]],
        responses_config: Dict[str, Dict[str, Any]]
    ) -> bool:
        """
        Save experiment suggestions to CSV file with proper formatting.
        
        Args:
            suggestions: List of parameter suggestion dictionaries
            filepath: Path to save CSV file
            params_config: Parameter configuration
            responses_config: Response configuration
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            if not suggestions:
                logger.warning("No suggestions to save")
                return False
            
            filepath = Path(filepath)
            suggestions_df = pd.DataFrame(suggestions)
            
            # Ensure all parameter columns are present
            param_names = list(params_config.keys())
            for param_name in param_names:
                if param_name not in suggestions_df.columns:
                    suggestions_df[param_name] = np.nan
            
            # Add response columns with NaN values for experimental results
            response_names = list(responses_config.keys())
            for response_name in response_names:
                if response_name not in suggestions_df.columns:
                    suggestions_df[response_name] = np.nan
            
            # Reorder columns: parameters first, then responses
            ordered_columns = param_names + response_names
            suggestions_df = suggestions_df.reindex(columns=ordered_columns)
            
            # Save to CSV
            return self.export_csv_data(suggestions_df, filepath)
            
        except Exception as e:
            logger.error(f"Error saving suggestions to CSV: {e}", exc_info=True)
            return False
    
    def validate_file_format(self, filepath: Union[str, Path]) -> Optional[str]:
        """
        Validate and detect file format.
        
        Args:
            filepath: Path to file
            
        Returns:
            Detected file format ('csv', 'excel', 'json', 'pickle') or None
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                logger.error(f"File does not exist: {filepath}")
                return None
            
            suffix = filepath.suffix.lower()
            
            if suffix == '.csv':
                return 'csv'
            elif suffix in ['.xlsx', '.xls']:
                return 'excel'
            elif suffix == '.json':
                return 'json'
            elif suffix in ['.pkl', '.pickle']:
                return 'pickle'
            else:
                logger.warning(f"Unknown file format: {suffix}")
                return None
                
        except Exception as e:
            logger.error(f"Error validating file format: {e}")
            return None
    
    def get_file_info(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about a file.
        
        Args:
            filepath: Path to file
            
        Returns:
            Dictionary with file information
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                return {"exists": False, "error": "File does not exist"}
            
            stat = filepath.stat()
            
            info = {
                "exists": True,
                "size_bytes": stat.st_size,
                "size_mb": stat.st_size / (1024 * 1024),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "format": self.validate_file_format(filepath),
                "name": filepath.name,
                "parent": str(filepath.parent)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return {"exists": False, "error": str(e)}
    
    def _clean_imported_data(self, data_df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean imported data by handling common issues.
        
        Args:
            data_df: Raw imported DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        try:
            cleaned_df = data_df.copy()
            
            # Remove completely empty rows
            cleaned_df = cleaned_df.dropna(how='all')
            
            # Clean column names (remove extra spaces, etc.)
            cleaned_df.columns = cleaned_df.columns.str.strip()
            
            # Convert numeric columns
            for column in cleaned_df.columns:
                if cleaned_df[column].dtype == 'object':
                    # Try to convert to numeric
                    numeric_data = pd.to_numeric(cleaned_df[column], errors='coerce')
                    
                    # If more than 50% of values are numeric, convert the column
                    valid_numeric = numeric_data.notna().sum()
                    total_values = len(cleaned_df[column].dropna())
                    
                    if total_values > 0 and valid_numeric / total_values >= 0.5:
                        cleaned_df[column] = numeric_data
            
            logger.debug(f"Data cleaning completed. Shape: {cleaned_df.shape}")
            return cleaned_df
            
        except Exception as e:
            logger.error(f"Error cleaning imported data: {e}")
            return data_df
    
    def clear_cache(self) -> None:
        """Clear file operation cache."""
        with self._lock:
            self._file_cache.clear()
        logger.debug("File controller cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get file cache statistics."""
        with self._lock:
            return {"cached_files": len(self._file_cache)}