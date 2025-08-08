"""
Validation utilities for prediction files.
"""

import os
import warnings
from typing import Dict, Any

import pandas as pd


def validate_predictions_file(file_path: str) -> Dict[str, Any]:
    """
    Validate and get information about a predictions CSV file.
    
    Args:
        file_path: Path to the CSV file to validate.
        
    Returns:
        Dictionary with file information and validation results.
        
    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If file format is invalid.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Check required columns
        required_columns = {'id', 'logits'}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}. "
                f"Required: {required_columns}. Found: {set(df.columns)}"
            )
        
        # Validate data types and format
        validation_results = {
            'file_path': file_path,
            'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
            'num_samples': len(df),
            'columns': list(df.columns),
            'has_labels': 'label' in df.columns,
            'validation_passed': True,
            'warnings': [],
            'errors': []
        }
        
        # Check ID column
        if df['id'].isnull().any():
            validation_results['errors'].append("ID column contains null values")
            validation_results['validation_passed'] = False
        
        if df['id'].duplicated().any():
            validation_results['warnings'].append("ID column contains duplicate values")
        
        # Check logits format
        sample_logits = df['logits'].iloc[0] if len(df) > 0 else None
        if sample_logits is not None:
            if isinstance(sample_logits, str) and ';' in sample_logits:
                try:
                    logits_values = [float(x) for x in sample_logits.split(';')]
                    validation_results['logits_dimension'] = len(logits_values)
                    validation_results['sample_logits_range'] = [min(logits_values), max(logits_values)]
                except ValueError:
                    validation_results['errors'].append("Logits contain non-numeric values")
                    validation_results['validation_passed'] = False
            else:
                validation_results['warnings'].append("Logits format may be invalid (should be semicolon-separated)")
        
        # Check for null logits
        if df['logits'].isnull().any():
            validation_results['errors'].append("Logits column contains null values")
            validation_results['validation_passed'] = False
        
        # Additional statistics
        if 'label' in df.columns:
            validation_results['num_classes'] = df['label'].nunique()
            validation_results['label_range'] = [df['label'].min(), df['label'].max()]
        
        # Sample data for inspection
        validation_results['sample_ids'] = df['id'].head(5).tolist()
        
        return validation_results
        
    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty")
    except pd.errors.ParserError as e:
        raise ValueError(f"Failed to parse CSV file: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error validating CSV file: {str(e)}")


def validate_logits_consistency(file_path: str, expected_dimension: int = 1000) -> bool:
    """
    Check if all logits in a file have consistent dimensions.
    
    Args:
        file_path: Path to the CSV file.
        expected_dimension: Expected dimension of logits (default 1000 for ImageNet).
        
    Returns:
        True if all logits have consistent dimensions, False otherwise.
    """
    try:
        df = pd.read_csv(file_path)
        
        inconsistent_count = 0
        for idx, logits_str in enumerate(df['logits'].head(100)):  # Check first 100 for speed
            if pd.isna(logits_str):
                inconsistent_count += 1
                continue
                
            try:
                logits_values = logits_str.split(';')
                if len(logits_values) != expected_dimension:
                    inconsistent_count += 1
            except (AttributeError, ValueError):
                inconsistent_count += 1
        
        if inconsistent_count > 0:
            warnings.warn(
                f"Found {inconsistent_count} samples with inconsistent logits dimensions "
                f"(expected {expected_dimension})"
            )
            return False
        
        return True
        
    except Exception as e:
        warnings.warn(f"Failed to validate logits consistency: {str(e)}")
        return False


def quick_file_check(file_path: str) -> bool:
    """
    Quick validation check for a predictions file.
    
    Args:
        file_path: Path to the file to check.
        
    Returns:
        True if basic validation passes, False otherwise.
    """
    try:
        if not os.path.exists(file_path):
            return False
        
        # Check file size (should be reasonable)
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb < 0.1 or size_mb > 2000:  # Between 100KB and 2GB
            return False
        
        # Try to read first few lines
        df_sample = pd.read_csv(file_path, nrows=5)
        required_columns = {'id', 'logits'}
        
        return required_columns.issubset(set(df_sample.columns))
        
    except Exception:
        return False
