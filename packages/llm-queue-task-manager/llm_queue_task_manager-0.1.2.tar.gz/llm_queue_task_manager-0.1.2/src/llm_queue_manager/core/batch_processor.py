"""Batch processor for managing LLM request processing cycles."""

import asyncio
import time
import os
from typing import Optional, Dict, Any
import logging

from .queue_manager import RedisQueueManager
from .models import QueuedRequest, TaskType, RequestStatus
from ..processors.base import BaseRequestProcessor

logger = logging.getLogger(__name__)

class RedisBatchProcessor:
    """
    Batch processor implementing intelligent 3-2-1 cycle processing.
    
    Processing cycle: 3 LOW → 2 MEDIUM → 1 LONG priority tasks
    Features:
    - Token quota management
    - Automatic retry handling
    - Graceful error recovery
    - Performance monitoring
    """
    
    def __init__(self, processor: BaseRequestProcessor, queue_manager: Optional[RedisQueueManager] = None):
        """
        Initialize batch processor.
        
        Args:
            processor: Request processor implementation
            queue_manager: Optional queue manager instance
        """
        self.processor = processor
        self.queue_manager = queue_manager or RedisQueueManager()
        self.is_processing = False
        self.processing_task: Optional[asyncio.Task] = None
        
        # Batch configuration (3-2-1 cycle)
        self.batch_config = {
            TaskType.LOW: int(os.getenv('LLM_QUEUE_BATCH_LOW_COUNT', 3)),
            TaskType.MEDIUM: int(os.getenv('LLM_QUEUE_BATCH_MEDIUM_COUNT', 2)),
            TaskType.LONG: int(os.getenv('LLM_QUEUE_BATCH_LONG_COUNT', 1))
        }
        
        # Processing state
        self.current_cycle_position = 0
        self.cycle_sequence = []
        self.consecutive_empty_cycles = 0
        self.max_empty_cycles = int(os.getenv('LLM_QUEUE_MAX_EMPTY_CYCLES', 5))
        
        # Quota exhaustion handling
        self.quota_exhausted_time = None
        self.quota_wait_duration = int(os.getenv('LLM_QUEUE_QUOTA_WAIT_DURATION', 65))
        self.consecutive_quota_failures = 0
        self.max_quota_failures = int(os.getenv('LLM_QUEUE_MAX_QUOTA_FAILURES', 3))
        
        # Performance tracking
        self.last_processed_time = time.time()
        self.requests_processed_this_cycle = 0
        self.total_requests_processed = 0
        self.processing_start_time = None
        
        # Error tracking
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        
        self._build_cycle_sequence()
        
        logger.info(f"Batch processor initialized with config: {self.batch_config}")
    
    def _build_cycle_sequence(self):
        """Build the processing sequence: LOW,LOW,LOW,MEDIUM,MEDIUM,LONG"""
        self.cycle_sequence = []
        for task_type, count in self.batch_config.items():
            self.cycle_sequence.extend([task_type] * count)
        
        logger.info(f"Built cycle sequence: {[t.value for t in self.cycle_sequence]} "
                   f"(total: {len(self.cycle_sequence)} steps)")
    
    async def start_processing(self):
        """Start the batch processing loop."""
        if self.is_processing:
            logger.warning("Processor already running")
            return
        
        self.is_processing = True
        self.processing_start_time = time.time()
        self.processing_task = asyncio.create_task(self._processing_loop())
        logger.info("Batch processor started")
    
    async def stop_processing(self):
        """Stop the batch processing loop gracefully."""
        logger.info("Stopping batch processor...")
        self.is_processing = False
        
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Batch processor stopped")
    
    async def _processing_loop(self):
        """Main processing loop implementing 3-2-1 batch logic with quota management."""
        logger.info("Starting processing loop")
        
        while self.is_processing:
            try:
                # Check if we're in quota exhaustion wait period
                if await self._should_wait_for_quota_reset():
                    await asyncio.sleep(5)  # Check every 5 seconds
                    continue
                
                # Get current task type from cycle
                current_task_type = self.cycle_sequence[self.current_cycle_position]
                
                # Try to process a request of this type
                result = await self._process_next_request(current_task_type)
                
                if result == "processed":
                    self._handle_successful_processing()
                elif result == "quota_exhausted":
                    await self._handle_quota_exhaustion()
                elif result == "no_request":
                    await self._handle_no_request()
                elif result == "error":
                    await self._handle_processing_error()
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                self.consecutive_errors += 1
                
                if self.consecutive_errors >= self.max_consecutive_errors:
                    logger.critical(f"Too many consecutive errors ({self.consecutive_errors}), "
                                   f"stopping processor")
                    break
                
                await asyncio.sleep(min(2 ** self.consecutive_errors, 60))  # Exponential backoff
    
    def _handle_successful_processing(self):
        """Handle successful request processing."""
        self.consecutive_empty_cycles = 0
        self.consecutive_quota_failures = 0
        self.consecutive_errors = 0
        self.requests_processed_this_cycle += 1
        self.total_requests_processed += 1
        self.last_processed_time = time.time()
        
        # Move to next position in cycle
        self.current_cycle_position = (self.current_cycle_position + 1) % len(self.cycle_sequence)
        
        # Log cycle completion
        if self.current_cycle_position == 0:
            logger.info(f"Completed full cycle, processed {self.requests_processed_this_cycle} requests")
            self.requests_processed_this_cycle = 0
    
    async def _handle_no_request(self):
        """Handle case when no request is available."""
        # Move to next position in cycle
        self.current_cycle_position = (self.current_cycle_position + 1) % len(self.cycle_sequence)
        
        # If we've gone through full cycle without processing anything
        if self.current_cycle_position == 0:
            self.consecutive_empty_cycles += 1
            
            if self.consecutive_empty_cycles >= self.max_empty_cycles:
                logger.debug("Multiple empty cycles, waiting longer...")
                await asyncio.sleep(5)  # Wait 5 seconds
                self.consecutive_empty_cycles = 0
            else:
                await asyncio.sleep(1)  # Wait 1 second
        else:
            await asyncio.sleep(0.1)  # Quick check next type
    
    async def _handle_processing_error(self):
        """Handle processing errors."""
        self.consecutive_errors += 1
        await asyncio.sleep(min(2 ** self.consecutive_errors, 10))  # Exponential backoff
    
    async def _should_wait_for_quota_reset(self) -> bool:
        """Check if we should wait for quota reset."""
        if not self.quota_exhausted_time:
            return False
        
        elapsed = time.time() - self.quota_exhausted_time
        
        # If enough time has passed, check if quota has reset
        if elapsed >= self.quota_wait_duration:
            # Test with a small token amount to see if quota has reset
            if self.queue_manager.check_token_budget(100):
                logger.info("Token quota has reset, resuming processing")
                self.quota_exhausted_time = None
                self.consecutive_quota_failures = 0
                return False
            else:
                # Quota still not available, extend wait time
                logger.warning("Quota still exhausted after wait period, extending wait")
                self.quota_exhausted_time = time.time()  # Reset wait timer
                return True
        
        # Still in wait period
        remaining_wait = self.quota_wait_duration - elapsed
        logger.debug(f"Waiting for quota reset, {remaining_wait:.0f}s remaining")
        return True
    
    async def _handle_quota_exhaustion(self):
        """Handle quota exhaustion scenario."""
        self.consecutive_quota_failures += 1
        current_time = time.time()
        
        if not self.quota_exhausted_time:
            self.quota_exhausted_time = current_time
            logger.warning(f"Token quota exhausted, waiting {self.quota_wait_duration}s for reset")
        
        # If we've had multiple consecutive failures, wait longer
        if self.consecutive_quota_failures >= self.max_quota_failures:
            extended_wait = self.quota_wait_duration + (self.consecutive_quota_failures * 30)
            logger.warning(f"Multiple quota failures, extending wait to {extended_wait}s")
            self.quota_exhausted_time = current_time - self.quota_wait_duration + extended_wait
    
    async def _process_next_request(self, task_type: TaskType) -> str:
        """
        Process next request of specified type.
        
        Args:
            task_type: Priority level to process
            
        Returns:
            Processing result: "processed", "quota_exhausted", "no_request", "error"
        """
        try:
            # Get next request
            request = await self.queue_manager.get_next_request(task_type)
            if not request:
                return "no_request"
            
            # Check if request was cancelled
            if request.status == RequestStatus.CANCELLED:
                logger.info(f"Skipping cancelled request {request.id}")
                return "processed"
            
            # Check token budget with buffer
            if not self.queue_manager.check_token_budget(request.estimated_tokens):
                logger.debug(f"Insufficient token budget for request {request.id} "
                           f"({request.estimated_tokens} tokens)")
                await self.queue_manager.requeue_request(request, increment_retry=False)
                return "quota_exhausted"
            
            # Reserve tokens
            if not self.queue_manager.reserve_tokens(request.estimated_tokens):
                logger.warning(f"Failed to reserve tokens for request {request.id}")
                await self.queue_manager.requeue_request(request, increment_retry=False)
                return "quota_exhausted"
            
            # Process the request
            success = await self._process_single_request(request)
            return "processed" if success else "error"
            
        except Exception as e:
            logger.error(f"Error processing {task_type.value} request: {e}")
            return "error"
    
    async def _process_single_request(self, request: QueuedRequest) -> bool:
        """
        Process a single request with error handling and retries.
        
        Args:
            request: Request to process
            
        Returns:
            True if processing completed (success or permanent failure)
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing {request.task_type.value} request {request.id} "
                       f"(tokens: {request.estimated_tokens}, retry: {request.retry_count})")
            
            # Validate request before processing
            if hasattr(self.processor, 'validate_request'):
                is_valid = await self.processor.validate_request(request.request_data)
                if not is_valid:
                    raise ValueError("Request validation failed")
            
            # Process the request
            result = await self.processor.process_request(request.request_data)
            
            # Mark as completed
            await self.queue_manager.complete_request(request, result=result)
            
            processing_time = time.time() - start_time
            logger.info(f"Successfully completed request {request.id} in {processing_time:.2f}s")
            return True
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Error processing request {request.id} after {processing_time:.2f}s: {error_msg}")
            
            # Handle retry logic
            if request.should_retry():
                logger.info(f"Retrying request {request.id} "
                           f"(attempt {request.retry_count + 1}/{request.max_retries})")
                await self.queue_manager.requeue_request(request, increment_retry=True)
                return True  # Consider as processed (will retry later)
            else:
                logger.error(f"Request {request.id} failed permanently after {request.max_retries} retries")
                await self.queue_manager.complete_request(request, error=error_msg)
                return True  # Consider as processed (failed permanently)
    
    def get_processor_status(self) -> Dict[str, Any]:
        """Get current processor status and performance metrics."""
        try:
            current_time = time.time()
            uptime = current_time - self.processing_start_time if self.processing_start_time else 0
            
            quota_status = "normal"
            if self.quota_exhausted_time:
                remaining_wait = max(0, self.quota_wait_duration - (current_time - self.quota_exhausted_time))
                quota_status = f"waiting_for_reset_{remaining_wait:.0f}s"
            
            # Calculate processing rate
            processing_rate = 0
            if uptime > 0:
                processing_rate = self.total_requests_processed / (uptime / 60)  # requests per minute
            
            return {
                'is_processing': self.is_processing,
                'uptime_seconds': uptime,
                'current_cycle_position': self.current_cycle_position,
                'current_task_type': self.cycle_sequence[self.current_cycle_position].value if self.cycle_sequence else None,
                'cycle_sequence': [t.value for t in self.cycle_sequence],
                'consecutive_empty_cycles': self.consecutive_empty_cycles,
                'requests_processed_this_cycle': self.requests_processed_this_cycle,
                'total_requests_processed': self.total_requests_processed,
                'last_processed_time': self.last_processed_time,
                'processing_rate_per_minute': round(processing_rate, 2),
                'batch_config': {k.value: v for k, v in self.batch_config.items()},
                'quota_status': quota_status,
                'consecutive_quota_failures': self.consecutive_quota_failures,
                'consecutive_errors': self.consecutive_errors,
                'health_status': self._get_health_status()
            }
            
        except Exception as e:
            logger.error(f"Error getting processor status: {e}")
            return {'is_processing': False, 'error': str(e)}
    
    def _get_health_status(self) -> str:
        """Get processor health status."""
        if not self.is_processing:
            return "stopped"
        elif self.consecutive_errors >= 5:
            return "degraded"
        elif self.quota_exhausted_time:
            return "quota_limited"
        elif self.consecutive_empty_cycles >= self.max_empty_cycles:
            return "idle"
        else:
            return "healthy"
    
    async def pause_processing(self):
        """Pause processing temporarily."""
        if self.is_processing and self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
            self.processing_task = None
            logger.info("Processing paused")
    
    async def resume_processing(self):
        """Resume processing after pause."""
        if self.is_processing and not self.processing_task:
            self.processing_task = asyncio.create_task(self._processing_loop())
            logger.info("Processing resumed")
    
    def update_batch_config(self, new_config: Dict[TaskType, int]):
        """
        Update batch configuration dynamically.
        
        Args:
            new_config: New batch configuration
        """
        self.batch_config.update(new_config)
        self._build_cycle_sequence()
        self.current_cycle_position = 0  # Reset cycle position
        logger.info(f"Batch configuration updated: {self.batch_config}")
