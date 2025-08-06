"""Redis-based queue manager for LLM processing tasks."""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
import logging
import os

from ..config.redis_config import get_redis_client
from .models import QueuedRequest, TaskType, RequestStatus

logger = logging.getLogger(__name__)

class RedisQueueManager:
    """
    Redis-based queue manager with token budget management and priority queuing.
    
    Features:
    - Priority-based queuing (low/medium/long)
    - Token budget management with per-minute quotas
    - Automatic retry handling
    - Comprehensive metrics tracking
    - Request lifecycle management
    """
    
    def __init__(self, redis_client=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the queue manager.
        
        Args:
            redis_client: Optional Redis client instance
            config: Optional configuration dictionary
        """
        self.redis = redis_client or get_redis_client()
        self.config = config or {}
        
        # Redis key patterns
        self.QUEUE_KEY = "llm_queue:queue:{task_type}"
        self.REQUEST_KEY = "llm_queue:request:{request_id}"
        self.TOKEN_USAGE_KEY = "llm_queue:tokens:used:{minute}"
        self.METRICS_KEY = "llm_queue:metrics:{metric_type}"
        self.PROCESSOR_STATE_KEY = "llm_queue:processor:state"
        
        # Token budget configuration
        self.TOTAL_TPM = int(os.getenv('LLM_QUEUE_TOTAL_TPM', self.config.get('total_tpm', 1_000_000)))
        self.API_ALLOCATION_PERCENT = float(os.getenv('LLM_QUEUE_API_ALLOCATION_PERCENT', 
                                                     self.config.get('api_allocation_percent', 40)))
        self.API_ALLOCATION = int(self.TOTAL_TPM * (self.API_ALLOCATION_PERCENT / 100))
        
        # Safety buffer to prevent quota exhaustion
        self.SAFETY_BUFFER_PERCENT = 10
        self.SAFETY_BUFFER = int(self.API_ALLOCATION * (self.SAFETY_BUFFER_PERCENT / 100))
        
        logger.info(f"Queue manager initialized - Total TPM: {self.TOTAL_TPM}, "
                   f"API Allocation: {self.API_ALLOCATION}, Safety Buffer: {self.SAFETY_BUFFER}")
    
    def _increment_metric_with_expiry(self, key: str, amount: int = 1, expiry_seconds: int = 86400):
        """Increment a metric and set/refresh its expiration time."""
        pipe = self.redis.pipeline()
        pipe.incr(key, amount)
        pipe.expire(key, expiry_seconds)
        pipe.execute()
    
    async def add_request(self, request: QueuedRequest) -> str:
        """
        Add request to appropriate priority queue.
        
        Args:
            request: QueuedRequest instance
            
        Returns:
            Request ID
            
        Raises:
            Exception: If adding to queue fails
        """
        try:
            request_key = self.REQUEST_KEY.format(request_id=request.id)
            queue_key = self.QUEUE_KEY.format(task_type=request.task_type.value)
            
            # Use pipeline for atomic operations
            pipe = self.redis.pipeline()
            
            # Store request details as hash
            request_dict = request.to_dict()
            pipe.hset(request_key, mapping=request_dict)
            pipe.expire(request_key, 86400)  # Expire after 24 hours
            
            # Add to priority queue (LPUSH for FIFO with RPOP)
            pipe.lpush(queue_key, request.id)
            
            # Execute atomically
            pipe.execute()
            
            # Update metrics
            self._increment_metric_with_expiry(self.METRICS_KEY.format(metric_type="total_queued"))
            self._increment_metric_with_expiry(f"llm_queue:metrics:queued:{request.task_type.value}")
            
            logger.info(f"Request {request.id} added to {request.task_type.value} queue "
                       f"(tokens: {request.estimated_tokens})")
            return request.id
            
        except Exception as e:
            logger.error(f"Error adding request to queue: {e}")
            raise
    
    async def get_next_request(self, task_type: TaskType) -> Optional[QueuedRequest]:
        """
        Get next request from specified priority queue.
        
        Args:
            task_type: Priority queue to check
            
        Returns:
            Next QueuedRequest or None if queue is empty
        """
        try:
            queue_key = self.QUEUE_KEY.format(task_type=task_type.value)
            
            # Pop request ID from queue (RPOP for FIFO)
            request_id = self.redis.rpop(queue_key)
            if not request_id:
                return None
            
            # Get request details
            request_key = self.REQUEST_KEY.format(request_id=request_id)
            request_data = self.redis.hgetall(request_key)
            
            if not request_data:
                logger.warning(f"Request {request_id} data not found")
                return None
            
            # Convert to QueuedRequest object
            request = QueuedRequest.from_dict(request_data)
            
            # Check if request was cancelled
            if request.status == RequestStatus.CANCELLED:
                logger.info(f"Skipping cancelled request {request_id}")
                return None
            
            # Update status to processing
            request.update_status(RequestStatus.PROCESSING)
            
            # Update in Redis
            pipe = self.redis.pipeline()
            pipe.hset(request_key, mapping={
                'status': request.status.value,
                'started_at': str(request.started_at)
            })
            pipe.incr(self.METRICS_KEY.format(metric_type="total_processing"))
            pipe.execute()
            
            logger.debug(f"Retrieved request {request_id} from {task_type.value} queue")
            return request
            
        except Exception as e:
            logger.error(f"Error getting next request from {task_type.value}: {e}")
            return None
    
    async def complete_request(self, request: QueuedRequest, result: Any = None, error: str = None):
        """
        Mark request as completed or failed.
        
        Args:
            request: QueuedRequest instance
            result: Processing result (if successful)
            error: Error message (if failed)
        """
        try:
            request_key = self.REQUEST_KEY.format(request_id=request.id)
            
            # Update request status
            if error:
                request.update_status(RequestStatus.FAILED, error=error)
                metric_type = "total_failed"
                logger.error(f"Request {request.id} failed: {error}")
            else:
                request.update_status(RequestStatus.COMPLETED, result=result)
                metric_type = "total_completed"
                logger.info(f"Request {request.id} completed successfully")
            
            # Prepare update data
            update_data = {
                'status': request.status.value,
                'completed_at': str(request.completed_at)
            }
            
            if error:
                update_data['error'] = str(error)[:1000]  # Limit error message length
            
            if result:
                # Serialize result
                try:
                    if isinstance(result, (dict, list)):
                        update_data['result'] = json.dumps(result)
                    else:
                        update_data['result'] = str(result)[:5000]  # Limit result length
                except Exception as e:
                    logger.warning(f"Failed to serialize result for request {request.id}: {e}")
                    update_data['result'] = "Result serialization failed"
            
            # Update in Redis
            pipe = self.redis.pipeline()
            pipe.hset(request_key, mapping=update_data)
            pipe.decr(self.METRICS_KEY.format(metric_type="total_processing"))
            pipe.execute()
            
            # Update metrics
            self._increment_metric_with_expiry(self.METRICS_KEY.format(metric_type=metric_type))
            self._increment_metric_with_expiry(f"llm_queue:metrics:{metric_type}:{request.task_type.value}")
            
        except Exception as e:
            logger.error(f"Error completing request {request.id}: {e}")
    
    async def requeue_request(self, request: QueuedRequest, increment_retry: bool = True):
        """
        Put request back in queue for retry.
        
        Args:
            request: QueuedRequest instance
            increment_retry: Whether to increment retry count
        """
        try:
            if increment_retry:
                request.retry_count += 1
            
            request.update_status(RequestStatus.QUEUED)
            request.started_at = None
            
            # Update in Redis
            request_key = self.REQUEST_KEY.format(request_id=request.id)
            queue_key = self.QUEUE_KEY.format(task_type=request.task_type.value)
            
            pipe = self.redis.pipeline()
            pipe.hset(request_key, mapping={
                'retry_count': str(request.retry_count),
                'status': request.status.value,
                'started_at': ''
            })
            
            # Add back to queue (LPUSH for priority, RPUSH for normal)
            if increment_retry:
                pipe.lpush(queue_key, request.id)  # Priority for retries
            else:
                pipe.rpush(queue_key, request.id)  # Back of queue for quota issues
            
            pipe.decr(self.METRICS_KEY.format(metric_type="total_processing"))
            pipe.execute()
            
            logger.info(f"Request {request.id} requeued (retry: {request.retry_count})")
            
        except Exception as e:
            logger.error(f"Error requeuing request {request.id}: {e}")
    
    async def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of specific request.
        
        Args:
            request_id: Request identifier
            
        Returns:
            Request status dictionary or None if not found
        """
        try:
            request_key = self.REQUEST_KEY.format(request_id=request_id)
            request_data = self.redis.hgetall(request_key)
            
            if not request_data:
                return None
            
            # Add computed fields
            created_at = float(request_data.get('created_at', 0))
            if created_at:
                request_data['age_seconds'] = time.time() - created_at
            
            started_at = request_data.get('started_at')
            completed_at = request_data.get('completed_at')
            if started_at and completed_at:
                try:
                    processing_time = float(completed_at) - float(started_at)
                    request_data['processing_time_seconds'] = processing_time
                except (ValueError, TypeError):
                    pass
            
            return request_data
            
        except Exception as e:
            logger.error(f"Error getting request status for {request_id}: {e}")
            return None
    
    async def cancel_request(self, request_id: str) -> bool:
        """
        Cancel a queued request.
        
        Args:
            request_id: Request identifier
            
        Returns:
            True if cancelled, False if not possible
        """
        try:
            request_key = self.REQUEST_KEY.format(request_id=request_id)
            request_data = self.redis.hgetall(request_key)
            
            if not request_data:
                return False
            
            current_status = request_data.get('status')
            if current_status == RequestStatus.QUEUED.value:
                self.redis.hset(request_key, 'status', RequestStatus.CANCELLED.value)
                logger.info(f"Request {request_id} cancelled")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling request {request_id}: {e}")
            return False
    
    def check_token_budget(self, estimated_tokens: int) -> bool:
        """
        Check if we have enough token budget with safety buffer.
        
        Args:
            estimated_tokens: Tokens needed for request
            
        Returns:
            True if budget is available
        """
        try:
            current_minute = int(time.time() // 60)
            token_key = self.TOKEN_USAGE_KEY.format(minute=current_minute)
            
            current_usage = int(self.redis.get(token_key) or 0)
            available = self.API_ALLOCATION - current_usage - self.SAFETY_BUFFER
            
            logger.debug(f"Token budget check - Current: {current_usage}, "
                        f"Available: {available}, Needed: {estimated_tokens}")
            return available >= estimated_tokens
            
        except Exception as e:
            logger.error(f"Error checking token budget: {e}")
            return False
    
    def reserve_tokens(self, tokens: int) -> bool:
        """
        Reserve tokens for processing.
        
        Args:
            tokens: Number of tokens to reserve
            
        Returns:
            True if reservation successful
        """
        try:
            current_minute = int(time.time() // 60)
            token_key = self.TOKEN_USAGE_KEY.format(minute=current_minute)
            
            # Use pipeline for atomic increment and expire
            pipe = self.redis.pipeline()
            pipe.incr(token_key, tokens)
            pipe.expire(token_key, 60)  # Expire after 1 minute
            results = pipe.execute()
            
            new_usage = results[0]
            success = new_usage <= self.API_ALLOCATION
            
            if success:
                logger.debug(f"Reserved {tokens} tokens, new usage: {new_usage}/{self.API_ALLOCATION}")
            else:
                logger.warning(f"Token reservation failed - would exceed budget: {new_usage}/{self.API_ALLOCATION}")
                # Rollback the increment
                self.redis.decr(token_key, tokens)
            
            return success
            
        except Exception as e:
            logger.error(f"Error reserving tokens: {e}")
            return False
    
    def get_queue_lengths(self) -> Dict[str, int]:
        """Get current queue lengths for all priority levels."""
        try:
            lengths = {}
            for task_type in TaskType:
                queue_key = self.QUEUE_KEY.format(task_type=task_type.value)
                lengths[task_type.value] = self.redis.llen(queue_key)
            return lengths
            
        except Exception as e:
            logger.error(f"Error getting queue lengths: {e}")
            return {task_type.value: 0 for task_type in TaskType}
    
    def get_current_token_usage(self) -> Dict[str, int]:
        """Get current minute's token usage."""
        try:
            current_minute = int(time.time() // 60)
            token_key = self.TOKEN_USAGE_KEY.format(minute=current_minute)
            current_usage = int(self.redis.get(token_key) or 0)
            
            return {
                'current_usage': current_usage,
                'api_allocation': self.API_ALLOCATION,
                'available': max(0, self.API_ALLOCATION - current_usage),
                'utilization_percent': (current_usage / self.API_ALLOCATION) * 100 if self.API_ALLOCATION > 0 else 0,
                'safety_buffer': self.SAFETY_BUFFER
            }
        except Exception as e:
            logger.error(f"Error getting token usage: {e}")
            return {
                'current_usage': 0, 
                'api_allocation': self.API_ALLOCATION, 
                'available': self.API_ALLOCATION, 
                'utilization_percent': 0,
                'safety_buffer': self.SAFETY_BUFFER
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive queue metrics."""
        try:
            metrics = {}
            
            # Basic metrics
            metrics['total_queued'] = int(self.redis.get(self.METRICS_KEY.format(metric_type="total_queued")) or 0)
            metrics['total_completed'] = int(self.redis.get(self.METRICS_KEY.format(metric_type="total_completed")) or 0)
            metrics['total_failed'] = int(self.redis.get(self.METRICS_KEY.format(metric_type="total_failed")) or 0)
            metrics['total_processing'] = int(self.redis.get(self.METRICS_KEY.format(metric_type="total_processing")) or 0)
            
            # Queue lengths
            metrics['queue_lengths'] = self.get_queue_lengths()
            metrics['total_in_queue'] = sum(metrics['queue_lengths'].values())
            
            # Token usage
            metrics['token_usage'] = self.get_current_token_usage()
            
            # Per-task-type metrics
            for task_type in TaskType:
                metrics[f'{task_type.value}_completed'] = int(
                    self.redis.get(f"llm_queue:metrics:total_completed:{task_type.value}") or 0
                )
                metrics[f'{task_type.value}_failed'] = int(
                    self.redis.get(f"llm_queue:metrics:total_failed:{task_type.value}") or 0
                )
                metrics[f'{task_type.value}_queued'] = int(
                    self.redis.get(f"llm_queue:metrics:queued:{task_type.value}") or 0
                )
            
            # Success rate
            total_processed = metrics['total_completed'] + metrics['total_failed']
            if total_processed > 0:
                metrics['success_rate_percent'] = (metrics['total_completed'] / total_processed) * 100
            else:
                metrics['success_rate_percent'] = 100
            
            # System health indicators
            metrics['system_health'] = self._calculate_system_health(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {}
    
    def _calculate_system_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate system health indicators."""
        try:
            token_util = metrics.get('token_usage', {}).get('utilization_percent', 0)
            total_in_queue = metrics.get('total_in_queue', 0)
            success_rate = metrics.get('success_rate_percent', 100)
            
            # Health score (0-100)
            health_score = 100
            
            # Deduct for high token utilization
            if token_util > 90:
                health_score -= 30
            elif token_util > 70:
                health_score -= 15
            
            # Deduct for large queue backlog
            if total_in_queue > 200:
                health_score -= 25
            elif total_in_queue > 100:
                health_score -= 10
            
            # Deduct for low success rate
            if success_rate < 90:
                health_score -= 20
            elif success_rate < 95:
                health_score -= 10
            
            health_score = max(0, health_score)
            
            # Determine status
            if health_score >= 80:
                status = "healthy"
            elif health_score >= 60:
                status = "warning"
            else:
                status = "critical"
            
            return {
                'status': status,
                'score': health_score,
                'token_utilization': token_util,
                'queue_backlog': total_in_queue,
                'success_rate': success_rate
            }
            
        except Exception as e:
            logger.error(f"Error calculating system health: {e}")
            return {'status': 'unknown', 'score': 0}
    
    def clear_all_queues(self):
        """Clear all queues - USE WITH CAUTION."""
        try:
            for task_type in TaskType:
                queue_key = self.QUEUE_KEY.format(task_type=task_type.value)
                self.redis.delete(queue_key)
            logger.warning("All queues cleared")
        except Exception as e:
            logger.error(f"Error clearing queues: {e}")
    
    def get_queue_info(self) -> Dict[str, Any]:
        """Get detailed queue information."""
        try:
            info = {
                'configuration': {
                    'total_tpm': self.TOTAL_TPM,
                    'api_allocation': self.API_ALLOCATION,
                    'api_allocation_percent': self.API_ALLOCATION_PERCENT,
                    'safety_buffer': self.SAFETY_BUFFER,
                    'safety_buffer_percent': self.SAFETY_BUFFER_PERCENT
                },
                'queues': {},
                'redis_info': {}
            }
            
            # Queue details
            for task_type in TaskType:
                queue_key = self.QUEUE_KEY.format(task_type=task_type.value)
                length = self.redis.llen(queue_key)
                
                info['queues'][task_type.value] = {
                    'length': length,
                    'description': self._get_queue_description(task_type),
                    'redis_key': queue_key
                }
            
            # Redis connection info
            try:
                redis_info = self.redis.info()
                info['redis_info'] = {
                    'connected_clients': redis_info.get('connected_clients', 0),
                    'used_memory_human': redis_info.get('used_memory_human', '0B'),
                    'redis_version': redis_info.get('redis_version', 'unknown')
                }
            except Exception:
                info['redis_info'] = {'status': 'connection_error'}
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting queue info: {e}")
            return {}
    
    def _get_queue_description(self, task_type: TaskType) -> str:
        """Get human-readable description for queue type."""
        descriptions = {
            TaskType.LOW: "< 15K tokens (Quick responses, simple prompts)",
            TaskType.MEDIUM: "15K-75K tokens (Standard requests, moderate complexity)",
            TaskType.LONG: "> 75K tokens (Complex prompts, detailed responses)"
        }
        return descriptions.get(task_type, "Unknown task type")

