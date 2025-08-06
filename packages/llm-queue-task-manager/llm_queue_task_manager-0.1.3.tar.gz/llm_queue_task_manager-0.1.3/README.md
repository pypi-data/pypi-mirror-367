
# LLM Queue Task Manager

A Redis-based queue system for managing LLM processing tasks with intelligent token budget management, priority queuing, and batch processing capabilities.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Redis](https://img.shields.io/badge/redis-4.0+-red.svg)](https://redis.io/)

## 🚀 Features

- **🎯 Priority-based Queuing**: Automatically categorizes tasks by estimated token usage (low/medium/long)
- **💰 Token Budget Management**: Prevents API quota exhaustion with intelligent rate limiting
- **⚡ Batch Processing**: Implements 3-2-1 cycle processing (3 low, 2 medium, 1 long priority tasks)
- **🔄 Retry Logic**: Automatic retry with exponential backoff for failed requests
- **📊 Real-time Monitoring**: Comprehensive metrics and status tracking
- **🔌 Extensible**: Easy to implement custom processors for different LLM providers
- **🏗️ Production Ready**: Built for high-throughput production environments
- **🛡️ Error Resilient**: Graceful error handling and recovery mechanisms

## 📦 Installation

### Using uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the package
uv add llm-queue-task-manager

# With optional dependencies for specific providers
uv add "llm-queue-task-manager[aws]"      # For AWS Bedrock
uv add "llm-queue-task-manager[openai]"   # For OpenAI
uv add "llm-queue-task-manager[fastapi]"  # For FastAPI integration
uv add "llm-queue-task-manager[all]"      # All optional dependencies


### Using pip

```bash
pip install llm-queue-task-manager

# With optional dependencies
pip install "llm-queue-task-manager[aws,openai,fastapi]"
```

## 🏃 Quick Start

### 1. Basic Usage

```python
import asyncio
from llm_queue_manager import (
    RedisQueueManager, 
    RedisBatchProcessor, 
    QueuedRequest,
    BaseRequestProcessor
)

# Create a custom processor
class MyLLMProcessor(BaseRequestProcessor):
    async def process_request(self, request_data):
        # Your LLM processing logic here
        prompt = request_data.get('prompt', '')
        # ... process with your LLM provider
        return {"response": f"Processed: {prompt}"}

# Initialize components
processor = MyLLMProcessor()
queue_manager = RedisQueueManager()
batch_processor = RedisBatchProcessor(processor, queue_manager)

# Start processing
async def main():
    await batch_processor.start_processing()
    
    # Submit a request
    request = QueuedRequest.create(
        request_data={'prompt': 'Hello, world!'},
        estimated_tokens=1000
    )
    
    request_id = await queue_manager.add_request(request)
    print(f"Request {request_id} queued")
    
    # Check status
    status = await queue_manager.get_request_status(request_id)
    print(f"Status: {status}")

asyncio.run(main())
```

### 2. AWS Bedrock Integration

```python
from llm_queue_manager import RedisQueueManager, RedisBatchProcessor, QueuedRequest
from llm_queue_manager.processors.examples import BedrockProcessor

# Initialize with Bedrock processor
processor = BedrockProcessor(region_name='us-east-1')
queue_manager = RedisQueueManager()
batch_processor = RedisBatchProcessor(processor, queue_manager)

async def process_claude_request():
    await batch_processor.start_processing()
    
    request = QueuedRequest.create(
        request_data={
            'messages': [
                {
                    'role': 'user',
                    'content': [{'text': 'Explain quantum computing'}]
                }
            ],
            'model': 'claude-3-sonnet',
            'max_tokens': 2000,
            'temperature': 0.7
        },
        estimated_tokens=10000
    )
    
    request_id = await queue_manager.add_request(request)
    return request_id
```

### 3. OpenAI Integration

```python
from llm_queue_manager.processors.examples import OpenAIProcessor

# Initialize with OpenAI processor
processor = OpenAIProcessor(api_key="your-openai-api-key")
queue_manager = RedisQueueManager()
batch_processor = RedisBatchProcessor(processor, queue_manager)

async def process_gpt_request():
    await batch_processor.start_processing()
    
    request = QueuedRequest.create(
        request_data={
            'messages': [
                {'role': 'user', 'content': 'Write a Python function for binary search'}
            ],
            'model': 'gpt-4',
            'max_tokens': 1000,
            'temperature': 0.3
        },
        estimated_tokens=5000
    )
    
    request_id = await queue_manager.add_request(request)
    return request_id
```

### 4. FastAPI Integration

```python
from fastapi import FastAPI
from llm_queue_manager import RedisQueueManager, RedisBatchProcessor, QueuedRequest
from your_processor import YourLLMProcessor

app = FastAPI()
processor = YourLLMProcessor()
queue_manager = RedisQueueManager()
batch_processor = RedisBatchProcessor(processor, queue_manager)

@app.on_event("startup")
async def startup():
    await batch_processor.start_processing()

@app.post("/submit")
async def submit_request(prompt: str, max_tokens: int = 1000):
    request = QueuedRequest.create(
        request_data={'prompt': prompt, 'max_tokens': max_tokens},
        estimated_tokens=max_tokens * 2
    )
    
    request_id = await queue_manager.add_request(request)
    return {"request_id": request_id, "status": "queued"}

@app.get("/status/{request_id}")
async def get_status(request_id: str):
    return await queue_manager.get_request_status(request_id)

@app.get("/metrics")
async def get_metrics():
    return queue_manager.get_metrics()
```

## ⚙️ Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_HOST=localhost                     # Redis host
REDIS_PORT=6379                         # Redis port
REDIS_DB=0                              # Redis database number
REDIS_PASSWORD=your_password            # Redis password (optional)
REDIS_MAX_CONNECTIONS=20                # Maximum Redis connections

# Queue Configuration
LLM_QUEUE_TOTAL_TPM=1000000            # Total tokens per minute
LLM_QUEUE_API_ALLOCATION_PERCENT=40    # Percentage for API allocation
LLM_QUEUE_BATCH_LOW_COUNT=3            # Low priority batch size
LLM_QUEUE_BATCH_MEDIUM_COUNT=2         # Medium priority batch size
LLM_QUEUE_BATCH_LONG_COUNT=1           # Long priority batch size
LLM_QUEUE_MAX_EMPTY_CYCLES=5           # Max empty cycles before longer wait
LLM_QUEUE_QUOTA_WAIT_DURATION=65       # Seconds to wait for quota reset
```

### Redis Setup

```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis:latest

# Using Docker Compose
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

## 🔧 Custom Processors

Create custom processors by extending `BaseRequestProcessor`:

```python
from llm_queue_manager import BaseRequestProcessor
import httpx

class CustomLLMProcessor(BaseRequestProcessor):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    def get_required_fields(self):
        return ['prompt', 'model']
    
    async def validate_request(self, request_data):
        # Custom validation logic
        if not request_data.get('prompt'):
            return False
        return await super().validate_request(request_data)
    
    async def process_request(self, request_data):
        # Custom processing logic
        response = await self.client.post(
            f"{self.base_url}/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "prompt": request_data['prompt'],
                "model": request_data.get('model', 'default'),
                "max_tokens": request_data.get('max_tokens', 1000)
            }
        )
        
        return response.json()
    
    async def estimate_tokens(self, request_data):
        # Custom token estimation
        prompt = request_data.get('prompt', '')
        max_tokens = request_data.get('max_tokens', 1000)
        return len(prompt) // 4 + max_tokens
    
    async def handle_error(self, error, request_data):
        # Custom error handling
        if "rate_limit" in str(error).lower():
            return None  # Trigger retry
        return {"error": str(error)}
```

## 📊 Monitoring and Metrics

### Queue Metrics

```python
metrics = queue_manager.get_metrics()

print(f"Total in queue: {metrics['total_in_queue']}")
print(f"Success rate: {metrics['success_rate_percent']}%")
print(f"Token utilization: {metrics['token_usage']['utilization_percent']}%")

# Per-priority metrics
for priority in ['low', 'medium', 'long']:
    completed = metrics[f'{priority}_completed']
    failed = metrics[f'{priority}_failed']
    print(f"{priority.upper()}: {completed} completed, {failed} failed")
```

### Processor Status

```python
status = batch_processor.get_processor_status()

print(f"Processing: {status['is_processing']}")
print(f"Current cycle: {status['current_cycle_position']}/6")
print(f"Current task type: {status['current_task_type']}")
print(f"Health status: {status['health_status']}")
print(f"Processing rate: {status['processing_rate_per_minute']} req/min")
```

### Health Checks

```python
# Test Redis connection
from llm_queue_manager.config import test_redis_connection
redis_healthy = test_redis_connection()

# Get system health
metrics = queue_manager.get_metrics()
health = metrics.get('system_health', {})
print(f"System status: {health.get('status', 'unknown')}")
print(f"Health score: {health.get('score', 0)}/100")
```

## 🏗️ Architecture

The system consists of several key components:

### Core Components

1. **QueuedRequest**: Data model for requests with automatic task type classification
2. **RedisQueueManager**: Handles queue operations, token budgeting, and metrics
3. **RedisBatchProcessor**: Implements the 3-2-1 batch processing cycle
4. **BaseRequestProcessor**: Abstract base class for implementing custom LLM processors
5. **TokenEstimator**: Estimates token usage for different request types

### Processing Flow

```
Request Submission → Token Estimation → Priority Classification → Queue Assignment
                                                                          ↓
Response Delivery ← Result Processing ← LLM API Call ← Batch Processing ← Queue Processing
```

### Priority System

Requests are automatically categorized into three priority levels:

- **🟢 Low Priority** (< 15K tokens): Quick responses, simple prompts
- **🟡 Medium Priority** (15K-75K tokens): Standard requests, moderate complexity  
- **🔴 Long Priority** (> 75K tokens): Complex prompts, detailed responses

The **3-2-1 processing cycle** ensures balanced throughput:
- 3 low priority requests
- 2 medium priority requests  
- 1 long priority request
- Repeat cycle

## 🛡️ Token Budget Management

The system implements intelligent token budget management:

- **📊 Per-minute quotas**: Tracks token usage per minute to prevent API limits
- **🛡️ Safety buffers**: Maintains 10% buffer to prevent quota exhaustion
- **⏸️ Automatic throttling**: Pauses processing when approaching limits
- **🔄 Quota reset detection**: Automatically resumes when quotas reset
- **📈 Usage tracking**: Comprehensive token usage analytics

## 🔄 Error Handling and Resilience

### Retry Strategies

- **Exponential backoff**: Increasing delays between retry attempts
- **Error classification**: Different handling for different error types
- **Quota-aware retries**: Special handling for rate limit errors
- **Maximum retry limits**: Prevents infinite retry loops

### Error Types

- **Rate Limiting**: Automatic retry with backoff
- **Quota Exhaustion**: Queue pausing until reset
- **Validation Errors**: Request modification and retry
- **Authentication**: Immediate failure with clear error
- **Server Errors**: Retry with exponential backoff
- **Network Timeouts**: Retry with connection pooling

## 📚 Examples

The package includes comprehensive examples:

- **`examples/basic_usage.py`**: Simple echo processor demonstration
- **`examples/fastapi_integration.py`**: Production FastAPI service
- **`examples/bedrock_example.py`**: AWS Bedrock with Claude models
- **`examples/openai_example.py`**: OpenAI GPT models with function calling

Run examples:

```bash
# Basic usage
python examples/basic_usage.py

# FastAPI service
python examples/fastapi_integration.py

# AWS Bedrock (requires AWS credentials)
python examples/bedrock_example.py

# OpenAI (requires OPENAI_API_KEY)
python examples/openai_example.py
```

## 🚀 Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy requirements
COPY pyproject.toml ./
RUN uv pip install --system -e ".[all]"

# Copy application
COPY . .

# Run application
CMD ["python", "-m", "your_app"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-queue-manager
spec:
  replicas: 3
  selector:
    matchLabels:
      app: llm-queue-manager
  template:
    metadata:
      labels:
        app: llm-queue-manager
    spec:
      containers:
      - name: app
        image: your-registry/llm-queue-manager:latest
        env:
        - name: REDIS_HOST
          value: "redis-service"
        - name: LLM_QUEUE_TOTAL_TPM
          value: "1000000"
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /v1/queue/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

### Monitoring Setup

```yaml
# Prometheus monitoring
- job_name: 'llm-queue-manager'
  static_configs:
  - targets: ['llm-queue-manager:8000']
  metrics_path: '/v1/queue/metrics'
  scrape_interval: 30s
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/AryamanGurjar/llm-queue-task-manager.git
cd llm-queue-task-manager

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras --dev

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run examples
uv run python examples/basic_usage.py
```

### Code Quality

```bash
# Format code
uv run black src/ examples/
uv run isort src/ examples/

# Type checking
uv run mypy src/

# Linting
uv run flake8 src/ examples/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Redis](https://redis.io/) for high-performance queuing
- Inspired by production LLM processing challenges
- Thanks to the open-source community for tools and libraries

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/AryamanGurjar/llm-queue-task-manager/issues)
- **Documentation**: [README](https://github.com/AryamanGurjar/llm-queue-task-manager/blob/master/README.md)
- **Env Documentation**: [ENV_DOC](https://github.com/AryamanGurjar/llm-queue-task-manager/blob/master/ENV_DOC.md)

---

**Made with ❤️ for the LLM community**
