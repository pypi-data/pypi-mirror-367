"""Base processor interface for LLM requests."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BaseRequestProcessor(ABC):
    """
    Base class for LLM request processors.
    
    This abstract class defines the interface that all LLM processors must implement.
    It provides hooks for request validation, processing, error handling, and token estimation.
    """
    
    @abstractmethod
    async def process_request(self, request_data: Dict[str, Any]) -> Any:
        """
        Process a single LLM request.
        
        This is the main method that must be implemented by all processors.
        It should handle the actual LLM API call and return the result.
        
        Args:
            request_data: Dictionary containing request parameters
            
        Returns:
            Processing result (can be any type - dict, string, etc.)
            
        Raises:
            Exception: If processing fails
        """
        pass
    
    async def validate_request(self, request_data: Dict[str, Any]) -> bool:
        """
        Validate request data before processing.
        
        Override this method to implement custom validation logic.
        
        Args:
            request_data: Dictionary containing request parameters
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation - check if request_data is not empty
            if not request_data:
                logger.warning("Empty request data")
                return False
            
            # Check for required fields (override in subclasses for specific requirements)
            required_fields = self.get_required_fields()
            for field in required_fields:
                if field not in request_data:
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating request: {e}")
            return False
    
    def get_required_fields(self) -> list:
        """
        Get list of required fields for this processor.
        
        Override in subclasses to specify required fields.
        
        Returns:
            List of required field names
        """
        return []
    
    async def estimate_tokens(self, request_data: Dict[str, Any]) -> int:
        """
        Estimate token usage for the request.
        
        Override this method for more accurate model-specific estimation.
        
        Args:
            request_data: Dictionary containing request parameters
            
        Returns:
            Estimated token count
        """
        try:
            from ..core.token_estimator import TokenEstimator
            return TokenEstimator.estimate_tokens(request_data)
        except Exception as e:
            logger.error(f"Error estimating tokens: {e}")
            return 5000  # Conservative fallback
    
    async def handle_error(self, error: Exception, request_data: Dict[str, Any]) -> Optional[Any]:
        """
        Handle processing errors with fallback strategies.
        
        Override this method to implement custom error handling and fallback logic.
        
        Args:
            error: The exception that occurred
            request_data: Original request data
            
        Returns:
            Fallback result or None to trigger retry
        """
        error_str = str(error).lower()
        
        # Common error handling patterns
        if "rate limit" in error_str or "quota" in error_str or "throttling" in error_str:
            logger.warning(f"Rate limiting detected: {error}")
            return None  # Trigger retry
        
        elif "timeout" in error_str:
            logger.warning(f"Timeout detected: {error}")
            return None  # Trigger retry
        
        elif "validation" in error_str or "invalid" in error_str:
            logger.error(f"Validation error (no retry): {error}")
            return {"error": "Request validation failed", "details": str(error)}
        
        elif "authentication" in error_str or "authorization" in error_str:
            logger.error(f"Auth error (no retry): {error}")
            return {"error": "Authentication failed", "details": str(error)}
        
        else:
            # Unknown error - let retry mechanism handle it
            logger.error(f"Unknown error: {error}")
            return None
    
    async def preprocess_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess request data before sending to LLM.
        
        Override this method to implement custom preprocessing logic.
        
        Args:
            request_data: Original request data
            
        Returns:
            Preprocessed request data
        """
        return request_data.copy()
    
    async def postprocess_result(self, result: Any, request_data: Dict[str, Any]) -> Any:
        """
        Postprocess result after receiving from LLM.
        
        Override this method to implement custom postprocessing logic.
        
        Args:
            result: Raw result from LLM
            request_data: Original request data
            
        Returns:
            Postprocessed result
        """
        return result
    
    def get_processor_info(self) -> Dict[str, Any]:
        """
        Get information about this processor.
        
        Override to provide processor-specific information.
        
        Returns:
            Dictionary with processor information
        """
        return {
            'name': self.__class__.__name__,
            'type': 'base',
            'version': '1.0.0',
            'supported_models': [],
            'required_fields': self.get_required_fields()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for this processor.
        
        Override to implement processor-specific health checks.
        
        Returns:
            Health check results
        """
        try:
            # Basic health check - just return healthy
            return {
                'status': 'healthy',
                'timestamp': __import__('time').time(),
                'processor': self.__class__.__name__
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': __import__('time').time(),
                'processor': self.__class__.__name__
            }
    
    def __str__(self) -> str:
        """String representation of the processor."""
        return f"{self.__class__.__name__}()"
    
    def __repr__(self) -> str:
        """Detailed representation of the processor."""
        info = self.get_processor_info()
        return f"{self.__class__.__name__}(type='{info['type']}', version='{info['version']}')"
