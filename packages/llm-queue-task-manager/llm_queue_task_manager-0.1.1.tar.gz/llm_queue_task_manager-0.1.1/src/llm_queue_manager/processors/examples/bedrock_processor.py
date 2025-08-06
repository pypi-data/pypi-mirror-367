"""AWS Bedrock processor implementation."""

import asyncio
import logging
from typing import Any, Dict, Optional, List
import json

try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from ..base import BaseRequestProcessor

logger = logging.getLogger(__name__)

class BedrockProcessor(BaseRequestProcessor):
    """
    AWS Bedrock processor for Claude and other models.
    
    Supports:
    - Claude 3 models (Haiku, Sonnet, Opus)
    - Automatic retry with exponential backoff
    - Token usage tracking
    - Error handling with fallback strategies
    """
    
    def __init__(self, region_name: str = 'us-east-1', **kwargs):
        """
        Initialize Bedrock processor.
        
        Args:
            region_name: AWS region
            **kwargs: Additional boto3 client configuration
        """
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for BedrockProcessor. Install with: pip install boto3")
        
        self.region_name = region_name
        self.client_config = kwargs
        self.bedrock_client = None
        
        # Model configurations
        self.model_configs = {
            'claude-3-haiku': {
                'model_id': 'anthropic.claude-3-haiku-20240307-v1:0',
                'max_tokens': 4096,
                'token_multiplier': 3
            },
            'claude-3-sonnet': {
                'model_id': 'anthropic.claude-3-sonnet-20240229-v1:0',
                'max_tokens': 4096,
                'token_multiplier': 4
            },
            'claude-3-opus': {
                'model_id': 'anthropic.claude-3-opus-20240229-v1:0',
                'max_tokens': 4096,
                'token_multiplier': 5
            },
            'claude-3.5-sonnet': {
                'model_id': 'anthropic.claude-3-5-sonnet-20240620-v1:0',
                'max_tokens': 4096,
                'token_multiplier': 4
            }
        }
        
        self._init_client()
    
    def _init_client(self):
        """Initialize Bedrock client with retry configuration."""
        try:
            config = Config(
                retries={'max_attempts': 3, 'mode': 'adaptive'},
                max_pool_connections=50,
                read_timeout=300,
                connect_timeout=60,
                **self.client_config
            )
            
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=self.region_name,
                config=config,
            )
            logger.info(f"Bedrock client initialized for region {self.region_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
    
    def get_required_fields(self) -> List[str]:
        """Get required fields for Bedrock requests."""
        return ['messages']
    
    async def validate_request(self, request_data: Dict[str, Any]) -> bool:
        """Validate Bedrock request data."""
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
                
                if message['role'] not in ['user', 'assistant']:
                    logger.warning(f"Invalid role: {message['role']}")
                    return False
            
            # Validate model if specified
            model = request_data.get('model')
            if model and model not in self.model_configs:
                logger.warning(f"Unsupported model: {model}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating Bedrock request: {e}")
            return False
    
    async def estimate_tokens(self, request_data: Dict[str, Any]) -> int:
        """Estimate tokens for Bedrock request."""
        try:
            messages = request_data.get('messages', [])
            system = request_data.get('system', [])
            max_tokens = request_data.get('max_tokens', 4000)
            model = request_data.get('model', 'claude-3-sonnet')
            
            # Calculate input tokens
            input_tokens = 0
            
            # Count message tokens
            for message in messages:
                content = message.get('content', [])
                if isinstance(content, str):
                    input_tokens += len(content) // 4
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            input_tokens += len(item['text']) // 4
            
            # Count system tokens
            if system:
                if isinstance(system, str):
                    input_tokens += len(system) // 4
                elif isinstance(system, list):
                    for item in system:
                        if isinstance(item, dict) and 'text' in item:
                            input_tokens += len(item['text']) // 4
            
            # Apply model-specific multiplier
            model_config = self.model_configs.get(model, self.model_configs['claude-3-sonnet'])
            multiplier = model_config['token_multiplier']
            
            total_tokens = input_tokens + (max_tokens * multiplier)
            return max(total_tokens, 1000)
            
        except Exception as e:
            logger.error(f"Error estimating tokens for Bedrock: {e}")
            return 25000  # Conservative fallback
    
    async def process_request(self, request_data: Dict[str, Any]) -> Any:
        """Process Bedrock request."""
        try:
            # Preprocess request
            processed_data = await self.preprocess_request(request_data)
            
            # Extract parameters
            model = processed_data.get('model', 'claude-3-sonnet')
            messages = processed_data.get('messages', [])
            system = processed_data.get('system', [])
            temperature = processed_data.get('temperature', 0.3)
            max_tokens = processed_data.get('max_tokens', 4000)
            tools = processed_data.get('tools', [])
            
            # Get model configuration
            model_config = self.model_configs.get(model)
            if not model_config:
                raise ValueError(f"Unsupported model: {model}")
            
            model_id = model_config['model_id']
            max_tokens = min(max_tokens, model_config['max_tokens'])
            
            logger.info(f'Starting Bedrock processing with {model} (model_id: {model_id})')
            
            # Prepare inference config
            inference_config = {
                "maxTokens": max_tokens,
                "temperature": temperature
            }
            
            # Add optional parameters
            if 'top_p' in processed_data:
                inference_config['topP'] = processed_data['top_p']
            if 'top_k' in processed_data:
                inference_config['topK'] = processed_data['top_k']
            
            # Prepare request parameters
            request_params = {
                'modelId': model_id,
                'messages': messages,
                'inferenceConfig': inference_config
            }
            
            # Add system message if provided
            if system:
                request_params['system'] = system
            
            # Add tools if provided
            if tools:
                request_params['toolConfig'] = {'tools': tools}
            
            # Call Bedrock with retry logic
            response = await self._call_bedrock_with_retry(request_params)
            
            # Process response
            result = await self._process_bedrock_response(response, processed_data)
            
            # Postprocess result
            final_result = await self.postprocess_result(result, request_data)
            
            logger.info(f"Bedrock processing completed successfully")
            return final_result
            
        except Exception as e:
            logger.error(f"Bedrock processing failed: {e}")
            
            # Try error handling
            fallback_result = await self.handle_error(e, request_data)
            if fallback_result is not None:
                return fallback_result
            
            raise
    
    async def _call_bedrock_with_retry(self, request_params: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """Call Bedrock API with retry logic."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Call Bedrock in executor to avoid blocking
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.bedrock_client.converse(**request_params)
                )
                return response
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                last_error = e
                
                if error_code in ['ThrottlingException', 'ServiceQuotaExceededException']:
                    # Exponential backoff for throttling
                    wait_time = (2 ** attempt) + (attempt * 0.1)
                    logger.warning(f"Throttling detected, waiting {wait_time:.1f}s before retry {attempt + 1}")
                    await asyncio.sleep(wait_time)
                    continue
                elif error_code in ['ValidationException', 'AccessDeniedException']:
                    # Don't retry these errors
                    logger.error(f"Non-retryable error: {error_code}")
                    raise
                else:
                    # Retry other errors with backoff
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt)
                        logger.warning(f"Bedrock error {error_code}, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                    continue
            
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)
                    logger.warning(f"Unexpected error, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                continue
        
        # All retries exhausted
        raise last_error
    
    async def _process_bedrock_response(self, response: Dict[str, Any], request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Bedrock API response."""
        try:
            output_message = response['output']['message']
            stop_reason = response.get('stopReason', 'end_turn')
            usage = response.get('usage', {})
            
            # Extract text content
            text_content = ""
            tool_uses = []
            
            for content in output_message.get('content', []):
                if 'text' in content:
                    text_content += content['text']
                elif 'toolUse' in content:
                    tool_uses.append(content['toolUse'])
            
            result = {
                "status": "completed",
                "model": request_data.get('model', 'claude-3-sonnet'),
                "response": text_content,
                "stop_reason": stop_reason,
                "usage": {
                    "input_tokens": usage.get('inputTokens', 0),
                    "output_tokens": usage.get('outputTokens', 0),
                    "total_tokens": usage.get('totalTokens', 0)
                },
                "tool_uses": tool_uses,
                "raw_response": output_message
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing Bedrock response: {e}")
            raise
    
    async def handle_error(self, error: Exception, request_data: Dict[str, Any]) -> Optional[Any]:
        """Handle Bedrock-specific errors."""
        error_str = str(error).lower()
        
        if isinstance(error, ClientError):
            error_code = error.response.get('Error', {}).get('Code', '')
            
            if error_code == 'ThrottlingException':
                logger.warning("Throttling detected, will retry")
                return None  # Trigger retry
            
            elif error_code == 'ValidationException':
                # Try to reduce request size
                logger.warning("Validation error, trying to reduce request size")
                reduced_request = await self._reduce_request_size(request_data)
                if reduced_request:
                    try:
                        return await self.process_request(reduced_request)
                    except Exception as e:
                        logger.error(f"Fallback processing also failed: {e}")
                
                return {
                    "status": "failed",
                    "error": "Request validation failed",
                    "details": str(error)
                }
            
            elif error_code in ['AccessDeniedException', 'UnauthorizedException']:
                return {
                    "status": "failed",
                    "error": "Access denied",
                    "details": "Check AWS credentials and permissions"
                }
            
            elif error_code == 'ModelNotReadyException':
                return {
                    "status": "failed",
                    "error": "Model not ready",
                    "details": "The requested model is not available"
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
                modified_data['max_tokens'] = min(original_max, 2048)
                logger.info(f"Reduced max_tokens from {original_max} to {modified_data['max_tokens']}")
            
            # Truncate messages if too long
            messages = modified_data.get('messages', [])
            for message in messages:
                content = message.get('content', [])
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            original_text = item['text']
                            if len(original_text) > 10000:
                                item['text'] = original_text[:10000] + "\n\n[Content truncated due to size limits]"
                                logger.info("Truncated message content for fallback processing")
            
            return modified_data
            
        except Exception as e:
            logger.error(f"Error reducing request size: {e}")
            return None
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Get Bedrock processor information."""
        return {
            'name': 'BedrockProcessor',
            'type': 'aws_bedrock',
            'version': '1.0.0',
            'region': self.region_name,
            'supported_models': list(self.model_configs.keys()),
            'required_fields': self.get_required_fields(),
            'features': [
                'claude_models',
                'tool_use',
                'system_messages',
                'retry_logic',
                'token_estimation'
            ]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for Bedrock processor."""
        try:
            # Test basic connectivity
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.bedrock_client.list_foundation_models()
            )
            
            return {
                'status': 'healthy',
                'timestamp': __import__('time').time(),
                'processor': 'BedrockProcessor',
                'region': self.region_name,
                'client_initialized': self.bedrock_client is not None
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': __import__('time').time(),
                'processor': 'BedrockProcessor',
                'region': self.region_name
            }

