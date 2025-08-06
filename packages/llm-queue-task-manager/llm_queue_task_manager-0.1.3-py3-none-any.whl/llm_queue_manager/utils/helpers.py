"""Helper utility functions."""

import time
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

def format_time_ago(seconds: float) -> str:
    """
    Format seconds into human readable time ago string.
    
    Args:
        seconds: Number of seconds
        
    Returns:
        Human readable time string
    """
    if seconds < 0:
        return "in the future"
    elif seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"

def calculate_success_rate(completed: int, failed: int) -> float:
    """
    Calculate success rate percentage.
    
    Args:
        completed: Number of completed requests
        failed: Number of failed requests
        
    Returns:
        Success rate as percentage (0-100)
    """
    total = completed + failed
    if total == 0:
        return 100.0
    return (completed / total) * 100

def format_bytes(bytes_value: Union[int, str]) -> str:
    """
    Format bytes into human readable string.
    
    Args:
        bytes_value: Number of bytes or string representation
        
    Returns:
        Human readable bytes string
    """
    try:
        if isinstance(bytes_value, str):
            # Try to extract number from string like "1024B" or "1.5K"
            import re
            match = re.match(r'([\d.]+)([KMGT]?B?)', bytes_value.upper())
            if match:
                num, unit = match.groups()
                bytes_value = float(num)
                if 'K' in unit:
                    bytes_value *= 1024
                elif 'M' in unit:
                    bytes_value *= 1024 ** 2
                elif 'G' in unit:
                    bytes_value *= 1024 ** 3
                elif 'T' in unit:
                    bytes_value *= 1024 ** 4
            else:
                bytes_value = int(bytes_value)
        
        bytes_value = int(bytes_value)
        
        if bytes_value < 1024:
            return f"{bytes_value}B"
        elif bytes_value < 1024 ** 2:
            return f"{bytes_value / 1024:.1f}KB"
        elif bytes_value < 1024 ** 3:
            return f"{bytes_value / (1024 ** 2):.1f}MB"
        elif bytes_value < 1024 ** 4:
            return f"{bytes_value / (1024 ** 3):.1f}GB"
        else:
            return f"{bytes_value / (1024 ** 4):.1f}TB"
            
    except (ValueError, TypeError):
        return str(bytes_value)

def validate_config(config: Dict[str, Any], required_fields: list, optional_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate
        required_fields: List of required field names
        optional_fields: Dictionary of optional fields with default values
        
    Returns:
        Validated configuration dictionary
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    validated_config = config.copy()
    
    # Check required fields
    for field in required_fields:
        if field not in validated_config:
            raise ValueError(f"Required configuration field missing: {field}")
        if validated_config[field] is None:
            raise ValueError(f"Required configuration field cannot be None: {field}")
    
    # Add optional fields with defaults
    if optional_fields:
        for field, default_value in optional_fields.items():
            if field not in validated_config:
                validated_config[field] = default_value
    
    return validated_config

def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def get_current_timestamp() -> float:
    """Get current timestamp."""
    return time.time()

def calculate_rate(count: int, time_period_seconds: float) -> float:
    """
    Calculate rate per minute.
    
    Args:
        count: Number of items
        time_period_seconds: Time period in seconds
        
    Returns:
        Rate per minute
    """
    if time_period_seconds <= 0:
        return 0.0
    return (count / time_period_seconds) * 60

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries.
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result

def deep_get(dictionary: Dict[str, Any], keys: str, default: Any = None) -> Any:
    """
    Get nested dictionary value using dot notation.
    
    Args:
        dictionary: Dictionary to search
        keys: Dot-separated key path (e.g., "user.profile.name")
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    try:
        for key in keys.split('.'):
            dictionary = dictionary[key]
        return dictionary
    except (KeyError, TypeError):
        return default

def sanitize_redis_key(key: str) -> str:
    """
    Sanitize string for use as Redis key.
    
    Args:
        key: Key to sanitize
        
    Returns:
        Sanitized key
    """
    # Replace problematic characters
    sanitized = key.replace(' ', '_').replace(':', '_').replace('*', '_')
    # Remove any remaining non-alphanumeric characters except underscore and hyphen
    sanitized = ''.join(c for c in sanitized if c.isalnum() or c in ['_', '-'])
    return sanitized

def calculate_exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Calculate exponential backoff delay.
    
    Args:
        attempt: Attempt number (0-based)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        
    Returns:
        Delay in seconds
    """
    delay = base_delay * (2 ** attempt)
    return min(delay, max_delay)

def is_valid_model_name(model_name: str, valid_models: list) -> bool:
    """
    Check if model name is valid.
    
    Args:
        model_name: Model name to check
        valid_models: List of valid model names
        
    Returns:
        True if valid
    """
    return model_name in valid_models

def extract_error_code(error: Exception) -> Optional[str]:
    """
    Extract error code from exception.
    
    Args:
        error: Exception to analyze
        
    Returns:
        Error code if found
    """
    error_str = str(error).lower()
    
    # Common error patterns
    if "rate limit" in error_str or "429" in error_str:
        return "RATE_LIMIT"
    elif "quota" in error_str or "quota exceeded" in error_str:
        return "QUOTA_EXCEEDED"
    elif "timeout" in error_str:
        return "TIMEOUT"
    elif "authentication" in error_str or "401" in error_str:
        return "AUTH_ERROR"
    elif "authorization" in error_str or "403" in error_str:
        return "PERMISSION_DENIED"
    elif "validation" in error_str or "400" in error_str:
        return "VALIDATION_ERROR"
    elif "not found" in error_str or "404" in error_str:
        return "NOT_FOUND"
    elif "server error" in error_str or "500" in error_str:
        return "SERVER_ERROR"
    else:
        return "UNKNOWN_ERROR"

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.0f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"

def create_health_summary(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create health summary from metrics.
    
    Args:
        metrics: System metrics
        
    Returns:
        Health summary
    """
    try:
        total_in_queue = metrics.get('total_in_queue', 0)
        success_rate = metrics.get('success_rate_percent', 100)
        token_util = metrics.get('token_usage', {}).get('utilization_percent', 0)
        
        # Determine overall health
        health_issues = []
        
        if token_util > 90:
            health_issues.append("High token utilization")
        if total_in_queue > 200:
            health_issues.append("Large queue backlog")
        if success_rate < 95:
            health_issues.append("Low success rate")
        
        if not health_issues:
            status = "healthy"
            score = 100
        elif len(health_issues) == 1:
            status = "warning"
            score = 75
        else:
            status = "critical"
            score = 50
        
        return {
            'status': status,
            'score': score,
            'issues': health_issues,
            'metrics': {
                'queue_size': total_in_queue,
                'success_rate': success_rate,
                'token_utilization': token_util
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating health summary: {e}")
        return {
            'status': 'unknown',
            'score': 0,
            'issues': ['Health check failed'],
            'error': str(e)
        }
