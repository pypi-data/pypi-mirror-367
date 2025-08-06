"""Token estimation utilities for different types of LLM requests."""

from typing import Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)

class TokenEstimator:
    """Utility class for estimating token usage in LLM requests."""
    
    # Token estimation constants
    CHARS_PER_TOKEN = 4  # Rough approximation: 4 characters ≈ 1 token
    MIN_TOKENS = 100     # Minimum token estimate
    
    # Model-specific multipliers for output tokens (input:output ratio)
    MODEL_MULTIPLIERS = {
        'gpt-3.5-turbo': 3,
        'gpt-4': 4,
        'gpt-4-turbo': 4,
        'claude-3-haiku': 3,
        'claude-3-sonnet': 4,
        'claude-3-opus': 5,
        'claude-3.5-sonnet': 4,
        'default': 4
    }
    
    @classmethod
    def estimate_tokens(cls, request_data: Dict[str, Any]) -> int:
        """
        Estimate total tokens for a generic LLM request.
        
        Args:
            request_data: Dictionary containing request parameters
            
        Returns:
            Estimated total token count
        """
        try:
            # Try different estimation methods based on available data
            if 'messages' in request_data:
                return cls._estimate_from_messages(request_data)
            elif 'prompt' in request_data:
                return cls._estimate_from_prompt(request_data)
            elif 'text' in request_data:
                return cls._estimate_from_text(request_data)
            else:
                # Fallback: estimate from all string values
                return cls._estimate_from_all_text(request_data)
                
        except Exception as e:
            logger.warning(f"Error estimating tokens: {e}")
            return cls._get_fallback_estimate(request_data)
    
    @classmethod
    def _estimate_from_messages(cls, request_data: Dict[str, Any]) -> int:
        """Estimate tokens from OpenAI-style messages format."""
        messages = request_data.get('messages', [])
        input_tokens = 0
        
        for message in messages:
            # Handle different message formats
            if isinstance(message, dict):
                content = message.get('content', '')
                if isinstance(content, str):
                    input_tokens += len(content) // cls.CHARS_PER_TOKEN
                elif isinstance(content, list):
                    # Handle multi-modal content
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            input_tokens += len(item['text']) // cls.CHARS_PER_TOKEN
            elif isinstance(message, str):
                input_tokens += len(message) // cls.CHARS_PER_TOKEN
        
        # Add system message tokens if present
        system = request_data.get('system', '')
        if system:
            if isinstance(system, str):
                input_tokens += len(system) // cls.CHARS_PER_TOKEN
            elif isinstance(system, list):
                for item in system:
                    if isinstance(item, dict) and 'text' in item:
                        input_tokens += len(item['text']) // cls.CHARS_PER_TOKEN
        
        # Get output token estimate
        max_tokens = request_data.get('max_tokens', 1000)
        model = request_data.get('model', 'default')
        
        # Apply model-specific multiplier
        multiplier = cls.MODEL_MULTIPLIERS.get(model, cls.MODEL_MULTIPLIERS['default'])
        total_tokens = input_tokens + (max_tokens * multiplier)
        
        return max(total_tokens, cls.MIN_TOKENS)
    
    @classmethod
    def _estimate_from_prompt(cls, request_data: Dict[str, Any]) -> int:
        """Estimate tokens from simple prompt format."""
        prompt = request_data.get('prompt', '')
        input_tokens = len(prompt) // cls.CHARS_PER_TOKEN
        
        max_tokens = request_data.get('max_tokens', 1000)
        model = request_data.get('model', 'default')
        
        multiplier = cls.MODEL_MULTIPLIERS.get(model, cls.MODEL_MULTIPLIERS['default'])
        total_tokens = input_tokens + (max_tokens * multiplier)
        
        return max(total_tokens, cls.MIN_TOKENS)
    
    @classmethod
    def _estimate_from_text(cls, request_data: Dict[str, Any]) -> int:
        """Estimate tokens from text field."""
        text = request_data.get('text', '')
        input_tokens = len(text) // cls.CHARS_PER_TOKEN
        
        max_tokens = request_data.get('max_tokens', 1000)
        total_tokens = input_tokens + max_tokens
        
        return max(total_tokens, cls.MIN_TOKENS)
    
    @classmethod
    def _estimate_from_all_text(cls, request_data: Dict[str, Any]) -> int:
        """Estimate tokens from all text content in request."""
        total_chars = 0
        
        def extract_text(obj):
            nonlocal total_chars
            if isinstance(obj, str):
                total_chars += len(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_text(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text(item)
        
        extract_text(request_data)
        input_tokens = total_chars // cls.CHARS_PER_TOKEN
        
        max_tokens = request_data.get('max_tokens', 1000)
        total_tokens = input_tokens + max_tokens
        
        return max(total_tokens, cls.MIN_TOKENS)
    
    @classmethod
    def _get_fallback_estimate(cls, request_data: Dict[str, Any]) -> int:
        """Conservative fallback estimate when other methods fail."""
        max_tokens = request_data.get('max_tokens', 1000)
        
        # Conservative estimate based on max_tokens
        if max_tokens < 1000:
            return 5000
        elif max_tokens < 4000:
            return 20000
        else:
            return 50000
    
    @classmethod
    def estimate_processing_time(cls, tokens: int, task_type: Optional[str] = None) -> float:
        """
        Estimate processing time in seconds based on tokens.
        
        Args:
            tokens: Estimated token count
            task_type: Optional task type for more accurate estimation
            
        Returns:
            Estimated processing time in seconds
        """
        if task_type:
            # Use task type for estimation
            if task_type == 'low':
                return 30.0
            elif task_type == 'medium':
                return 90.0
            else:  # long
                return 180.0
        else:
            # Use token count
            if tokens < 15000:
                return 30.0
            elif tokens < 75000:
                return 90.0
            else:
                return 180.0
    
    @classmethod
    def validate_token_estimate(cls, tokens: int, request_data: Dict[str, Any]) -> int:
        """
        Validate and adjust token estimate based on request data.
        
        Args:
            tokens: Initial token estimate
            request_data: Request data for validation
            
        Returns:
            Validated token estimate
        """
        # Ensure minimum
        tokens = max(tokens, cls.MIN_TOKENS)
        
        # Check against max_tokens if specified
        max_tokens = request_data.get('max_tokens')
        if max_tokens:
            # Ensure estimate is reasonable compared to max_tokens
            min_estimate = max_tokens * 2  # At least 2x max_tokens
            tokens = max(tokens, min_estimate)
        
        # Cap at reasonable maximum
        max_estimate = 1_000_000  # 1M tokens max
        tokens = min(tokens, max_estimate)
        
        return tokens
    
    @classmethod
    def estimate_for_model(cls, request_data: Dict[str, Any], model_name: str) -> int:
        """
        Estimate tokens for a specific model.
        
        Args:
            request_data: Request data
            model_name: Name of the LLM model
            
        Returns:
            Model-specific token estimate
        """
        # Add model to request data for estimation
        enhanced_data = request_data.copy()
        enhanced_data['model'] = model_name
        
        return cls.estimate_tokens(enhanced_data)
