"""Core data models for the LLM queue system."""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, Optional, Union
import time
import json
from uuid import uuid4

class TaskType(Enum):
    """Task priority types based on estimated token usage."""
    LOW = "low"        # < 15k tokens - Quick responses, simple prompts
    MEDIUM = "medium"  # 15k-75k tokens - Standard requests
    LONG = "long"      # > 75k tokens - Complex, detailed requests

class RequestStatus(Enum):
    """Request processing status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class QueuedRequest:
    """
    Represents a queued LLM processing request.
    
    This class handles the complete lifecycle of an LLM request from submission
    to completion, including retry logic and status tracking.
    """
    
    id: str
    task_type: TaskType
    request_data: Dict[str, Any]
    estimated_tokens: int
    created_at: float
    status: RequestStatus = RequestStatus.QUEUED
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    result: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(
        cls, 
        request_data: Dict[str, Any], 
        estimated_tokens: int, 
        max_retries: int = 3,
        task_type: Optional[TaskType] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'QueuedRequest':
        """
        Create a new queued request with automatic task type classification.
        
        Args:
            request_data: Dictionary containing request parameters
            estimated_tokens: Estimated token usage for the request
            max_retries: Maximum number of retry attempts
            task_type: Override automatic task type classification
            metadata: Additional metadata for the request
            
        Returns:
            New QueuedRequest instance
        """
        if task_type is None:
            task_type = cls._determine_task_type(estimated_tokens)
            
        return cls(
            id=str(uuid4()),
            task_type=task_type,
            request_data=request_data,
            estimated_tokens=estimated_tokens,
            created_at=time.time(),
            max_retries=max_retries,
            metadata=metadata or {}
        )
    
    @staticmethod
    def _determine_task_type(tokens: int) -> TaskType:
        """
        Determine task type based on token count.
        
        Args:
            tokens: Estimated token count
            
        Returns:
            Appropriate TaskType
        """
        if tokens < 15000:
            return TaskType.LOW
        elif tokens < 75000:
            return TaskType.MEDIUM
        else:
            return TaskType.LONG
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for Redis storage.
        
        Returns:
            Dictionary representation suitable for Redis
        """
        data = asdict(self)
        data['task_type'] = self.task_type.value
        data['status'] = self.status.value
        
        # Serialize complex fields
        for field in ['request_data', 'result', 'metadata']:
            if data.get(field) is not None:
                try:
                    data[field] = json.dumps(data[field])
                except (TypeError, ValueError):
                    # Fallback for non-serializable objects
                    data[field] = json.dumps({str(k): str(v) for k, v in data[field].items()})
            else:
                data[field] = json.dumps({})
        
        # Handle None values for Redis compatibility
        for key, value in data.items():
            if value is None:
                if key in ['started_at', 'completed_at']:
                    data[key] = 0.0
                elif key in ['retry_count', 'max_retries', 'estimated_tokens']:
                    data[key] = 0
                else:
                    data[key] = ""
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueuedRequest':
        """
        Create from dictionary (Redis data).
        
        Args:
            data: Dictionary from Redis
            
        Returns:
            QueuedRequest instance
        """
        # Convert enums
        data['task_type'] = TaskType(data['task_type'])
        data['status'] = RequestStatus(data['status'])
        
        # Deserialize complex fields
        for field in ['request_data', 'result', 'metadata']:
            if data.get(field) and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    data[field] = {}
            elif not data.get(field):
                data[field] = {} if field == 'metadata' else None
        
        # Convert timestamps
        for field in ['created_at', 'started_at', 'completed_at']:
            if data.get(field) is not None:
                if isinstance(data[field], str):
                    try:
                        value = float(data[field])
                        data[field] = value if value != 0.0 else None
                    except ValueError:
                        data[field] = None
                elif data[field] == 0.0:
                    data[field] = None
        
        # Convert integers
        for field in ['estimated_tokens', 'retry_count', 'max_retries']:
            if data.get(field) and isinstance(data[field], str):
                try:
                    data[field] = int(data[field])
                except ValueError:
                    data[field] = 0
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'QueuedRequest':
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def get_age_seconds(self) -> float:
        """Get age of request in seconds."""
        return time.time() - self.created_at
    
    def get_processing_time(self) -> Optional[float]:
        """Get processing time if completed."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    def should_retry(self) -> bool:
        """Check if request should be retried."""
        return self.retry_count < self.max_retries and self.status == RequestStatus.FAILED
    
    def get_priority_score(self) -> int:
        """
        Get priority score for queue ordering.
        Lower scores = higher priority.
        """
        base_score = {
            TaskType.LOW: 1,
            TaskType.MEDIUM: 2, 
            TaskType.LONG: 3
        }[self.task_type]
        
        # Increase priority for retries
        retry_bonus = max(0, 3 - self.retry_count)
        
        # Increase priority for older requests
        age_bonus = min(2, int(self.get_age_seconds() / 300))  # +1 every 5 minutes
        
        return base_score - retry_bonus - age_bonus
    
    def update_status(self, status: RequestStatus, error: Optional[str] = None, result: Optional[Any] = None):
        """Update request status with timestamp."""
        self.status = status
        
        if status == RequestStatus.PROCESSING:
            self.started_at = time.time()
        elif status in [RequestStatus.COMPLETED, RequestStatus.FAILED, RequestStatus.CANCELLED]:
            self.completed_at = time.time()
            
        if error:
            self.error = error
        if result is not None:
            self.result = result
    
    def __str__(self) -> str:
        """String representation."""
        return f"QueuedRequest(id={self.id[:8]}, type={self.task_type.value}, status={self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (f"QueuedRequest(id='{self.id}', task_type={self.task_type}, "
                f"status={self.status}, tokens={self.estimated_tokens}, "
                f"retries={self.retry_count}/{self.max_retries})")
