"""OpenAI processor implementation."""

import asyncio
import logging
from typing import Any, Dict, Optional, List
import json

try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..base import BaseRequestProcessor

logger = logging.getLogger(__name__)

class OpenAIProcessor(BaseRequestProcessor):
    """
    OpenAI processor for GPT models.
    
    Supports:
    - GPT-3.5 and GPT-4 models
    - Function calling
    - Streaming responses
    - Automatic retry with exponential backoff
    - Token usage tracking
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        """
        Initialize OpenAI processor.
        
        Args:
            api_key: OpenAI API key (if not provided, will use OPENAI_API_KEY env var)
            base_url: Custom base URL for API calls
            **kwargs: Additional client configuration
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai is required for OpenAIProcessor. Install with: pip install openai")
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )
        
        # Model configurations
        self.model_configs = {
            'gpt-3.5-turbo': {
                'max_tokens': 4096,
                'token_multiplier': 3,
                'supports_functions': True
            },
            'gpt-3.5-turbo-16k': {
                'max_tokens': 16384,
                'token_multiplier': 3,
                'supports_functions': True
            },
            'gpt-4': {
                'max_tokens': 8192,
                'token_multiplier': 4,
                'supports_functions': True
            },
            'gpt-4-turbo': {
                'max_tokens': 4096,
                'token_multiplier': 4,
                'supports_functions': True
            },
            'gpt-4o': {
                'max_tokens': 4096,
                'token_multiplier': 4,
                'supports_functions': True
            },
            'gpt-4o-mini': {
                'max_tokens': 16384,
                'token_multiplier': 3,
                'supports_functions': True
            }
        }
        
        logger.info("OpenAI processor initialized")
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for OpenAI requests."""
        return ['messages']
    
    async def validate_request(self, request_data: Dict[str, Any]) -> bool:
        """Validate OpenAI request data."""
        if not await super().validate_request(request_data):
            return False
        
        try:
            messages = request_data.get('messages', [])
            if not messages:
                logger.warning("No messages provided")
                return False
            
            # Validate message format
            for message in messages:
                if not isinstance(message, dict):
                    logger.warning("Invalid message format - must be dict")
                    return False
                
                if 'role' not in message or 'content' not in message:
                    logger.warning("Message missing required fields: role, content")
                    return False
                
                if message['role'] not in ['system', 'user', 'assistant', 'function', 'tool']:
                    logger.warning(f"Invalid role: {message['role']}")
                    return False
            
            # Validate model if specified
            model = request_data.get('model', 'gpt-3.5-turbo')
            if model not in self.model_configs:
                logger.warning(f"Unsupported model: {model}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating OpenAI request: {e}")
            return False
    
    async def estimate_tokens(self, request_data: Dict[str, Any]) -> int:
        """Estimate tokens for OpenAI request."""
        try:
            messages = request_data.get('messages', [])
            max_tokens = request_data.get('max_tokens', 1000)
            model = request_data.get('model', 'gpt-3.5-turbo')
            
            # Calculate input tokens
            input_tokens = 0
            
            for message in messages:
                content = message.get('content', '')
                if isinstance(content, str):
                    input_tokens += len(content) // 4
                elif isinstance(content, list):
                    # Handle multi-modal content
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            input_tokens += len(item.get('text', '')) // 4
            
            # Apply model-specific multiplier
            model_config = self.model_configs.get(model, self.model_configs['gpt-3.5-turbo'])
            multiplier = model_config['token_multiplier']
            
            total_tokens = input_tokens + (max_tokens * multiplier)
            return max(total_tokens, 1000)
            
        except Exception as e:
            logger.error(f"Error estimating tokens for OpenAI: {e}")
            return 10000  # Conservative fallback
    
    async def process_request(self, request_data: Dict[str, Any]) -> Any:
        """Process OpenAI request."""
        try:
            # Preprocess request
            processed_data = await self.preprocess_request(request_data)
            
            # Extract parameters
            model = processed_data.get('model', 'gpt-3.5-turbo')
            messages = processed_data.get('messages', [])
            temperature = processed_data.get('temperature', 0.3)
            max_tokens = processed_data.get('max_tokens', 1000)
            functions = processed_data.get('functions', [])
            tools = processed_data.get('tools', [])
            stream = processed_data.get('stream', False)
            
            # Get model configuration
            model_config = self.model_configs.get(model)
            if not model_config:
                raise ValueError(f"Unsupported model: {model}")
            
            max_tokens = min(max_tokens, model_config['max_tokens'])
            
            logger.info(f'Starting OpenAI processing with {model}')
            
            # Prepare request parameters
            request_params = {
                'model': model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            # Add optional parameters
            if 'top_p' in processed_data:
                request_params['top_p'] = processed_data['top_p']
            if 'frequency_penalty' in processed_data:
                request_params['frequency_penalty'] = processed_data['frequency_penalty']
            if 'presence_penalty' in processed_data:
                request_params['presence_penalty'] = processed_data['presence_penalty']
            
            # Add functions/tools if provided and supported
            if model_config['supports_functions']:
                if tools:
                    request_params['tools'] = tools
                elif functions:
                    # Convert legacy functions to tools format
                    request_params['tools'] = [
                        {'type': 'function', 'function': func} for func in functions
                    ]
            
            # Process request (streaming or non-streaming)
            if stream:
                result = await self._process_streaming_request(request_params, processed_data)
            else:
                result = await self._process_standard_request(request_params, processed_data)
            
            # Postprocess result
            final_result = await self.postprocess_result(result, request_data)
            
            logger.info(f"OpenAI processing completed successfully")
            return final_result
            
        except Exception as e:
            logger.error(f"OpenAI processing failed: {e}")
            
            # Try error handling
            fallback_result = await self.handle_error(e, request_data)
            if fallback_result is not None:
                return fallback_result
            
            raise
    
    async def _process_standard_request(self, request_params: Dict[str, Any], original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process standard (non-streaming) OpenAI request."""
        try:
            response = await self._call_openai_with_retry(request_params)
            
            choice = response.choices[0]
            message = choice.message
            
            result = {
                "status": "completed",
                "model": request_params['model'],
                "response": message.content or "",
                "finish_reason": choice.finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            # Handle function/tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": call.id,
                        "type": call.type,
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments
                        }
                    } for call in message.tool_calls
                ]
            elif hasattr(message, 'function_call') and message.function_call:
                result["function_call"] = {
                    "name": message.function_call.name,
                    "arguments": message.function_call.arguments
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing standard OpenAI request: {e}")
            raise
    
    async def _process_streaming_request(self, request_params: Dict[str, Any], original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process streaming OpenAI request."""
        try:
            request_params['stream'] = True
            
            response_content = ""
            function_calls = []
            usage_info = None
            finish_reason = None
            
            async for chunk in await self.client.chat.completions.create(**request_params):
                if chunk.choices:
                    choice = chunk.choices[0]
                    delta = choice.delta
                    
                    if delta.content:
                        response_content += delta.content
                    
                    if hasattr(delta, 'function_call') and delta.function_call:
                        # Handle function calls in streaming
                        function_calls.append(delta.function_call)
                    
                    if choice.finish_reason:
                        finish_reason = choice.finish_reason
                
                if hasattr(chunk, 'usage') and chunk.usage:
                    usage_info = chunk.usage
            
            result = {
                "status": "completed",
                "model": request_params['model'],
                "response": response_content,
                "finish_reason": finish_reason,
                "streaming": True
            }
            
            if usage_info:
                result["usage"] = {
                    "prompt_tokens": usage_info.prompt_tokens,
                    "completion_tokens": usage_info.completion_tokens,
                    "total_tokens": usage_info.total_tokens
                }
            
            if function_calls:
                result["function_calls"] = function_calls
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing streaming OpenAI request: {e}")
            raise
    
    async def _call_openai_with_retry(self, request_params: Dict[str, Any], max_retries: int = 3):
        """Call OpenAI API with retry logic."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(**request_params)
                return response
                
            except openai.RateLimitError as e:
                last_error = e
                wait_time = (2 ** attempt) + (attempt * 0.1)
                logger.warning(f"Rate limit hit, waiting {wait_time:.1f}s before retry {attempt + 1}")
                await asyncio.sleep(wait_time)
                continue
                
            except openai.APITimeoutError as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)
                    logger.warning(f"Timeout error, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                continue
                
            except openai.APIError as e:
                last_error = e
                if e.status_code in [500, 502, 503, 504]:
                    # Server errors - retry
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt)
                        logger.warning(f"Server error {e.status_code}, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                    continue
                else:
                    # Client errors - don't retry
                    raise
                    
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)
                    logger.warning(f"Unexpected error, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                continue
        
        # All retries exhausted
        raise last_error
    
    async def handle_error(self, error: Exception, request_data: Dict[str, Any]) -> Optional[Any]:
        """Handle OpenAI-specific errors."""
        if isinstance(error, openai.RateLimitError):
            logger.warning("Rate limit error, will retry")
            return None  # Trigger retry
        
        elif isinstance(error, openai.InvalidRequestError):
            # Try to reduce request size
            logger.warning("Invalid request error, trying to reduce request size")
            reduced_request = await self._reduce_request_size(request_data)
            if reduced_request:
                try:
                    return await self.process_request(reduced_request)
                except Exception as e:
                    logger.error(f"Fallback processing also failed: {e}")
            
            return {
                "status": "failed",
                "error": "Invalid request",
                "details": str(error)
            }
        
        elif isinstance(error, openai.AuthenticationError):
            return {
                "status": "failed",
                "error": "Authentication failed",
                "details": "Check OpenAI API key"
            }
        
        elif isinstance(error, openai.PermissionDeniedError):
            return {
                "status": "failed",
                "error": "Permission denied",
                "details": "Check API key permissions"
            }
        
        # Call parent error handler for common patterns
        return await super().handle_error(error, request_data)
    
    async def _reduce_request_size(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Reduce request size to avoid validation errors."""
        try:
            modified_data = request_data.copy()
            
            # Reduce max_tokens
            if 'max_tokens' in modified_data:
                original_max = modified_data['max_tokens']
                modified_data['max_tokens'] = min(original_max, 1000)
                logger.info(f"Reduced max_tokens from {original_max} to {modified_data['max_tokens']}")
            
            # Truncate messages if too long
            messages = modified_data.get('messages', [])
            for message in messages:
                content = message.get('content', '')
                if isinstance(content, str) and len(content) > 8000:
                    message['content'] = content[:8000] + "\n\n[Content truncated due to size limits]"
                    logger.info("Truncated message content for fallback processing")
            
            return modified_data
            
        except Exception as e:
            logger.error(f"Error reducing request size: {e}")
            return None
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Get OpenAI processor information."""
        return {
            'name': 'OpenAIProcessor',
            'type': 'openai',
            'version': '1.0.0',
            'supported_models': list(self.model_configs.keys()),
            'required_fields': self.get_required_fields(),
            'features': [
                'gpt_models',
                'function_calling',
                'streaming',
                'retry_logic',
                'token_estimation'
            ]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for OpenAI processor."""
        try:
            # Test basic connectivity with a minimal request
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            
            return {
                'status': 'healthy',
                'timestamp': __import__('time').time(),
                'processor': 'OpenAIProcessor',
                'test_response_id': response.id
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': __import__('time').time(),
                'processor': 'OpenAIProcessor'
            }
