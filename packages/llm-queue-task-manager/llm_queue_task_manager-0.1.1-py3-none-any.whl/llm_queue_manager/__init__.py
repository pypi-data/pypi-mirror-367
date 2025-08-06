"""
LLM Queue Task Manager

A Redis-based queue system for managing LLM processing tasks with intelligent token budget management,
priority queuing, and batch processing capabilities.
"""

from .core.models import QueuedRequest, TaskType, RequestStatus
from .core.queue_manager import RedisQueueManager
from .core.batch_processor import RedisBatchProcessor
from .core.token_estimator import TokenEstimator
from .processors.base import BaseRequestProcessor
from .config.redis_config import RedisConfig, get_redis_client
from .utils.helpers import format_time_ago, calculate_success_rate

__version__ = "0.1.0"
__author__ = "LLM Queue Manager Team"
__email__ = "contact@example.com"

__all__ = [
    # Core models
    "QueuedRequest",
    "TaskType", 
    "RequestStatus",
    
    # Queue management
    "RedisQueueManager",
    "RedisBatchProcessor",
    "TokenEstimator",
    
    # Processor interface
    "BaseRequestProcessor",
    
    # Configuration
    "RedisConfig",
    "get_redis_client",
    
    # Utilities
    "format_time_ago",
    "calculate_success_rate",
]
