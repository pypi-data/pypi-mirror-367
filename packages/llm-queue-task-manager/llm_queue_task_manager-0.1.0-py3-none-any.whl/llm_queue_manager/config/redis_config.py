"""Redis configuration and client management."""

import os
import logging
from typing import Optional
import redis
from redis.connection import ConnectionPool

logger = logging.getLogger(__name__)

class RedisConfig:
    """Redis configuration manager."""
    
    def __init__(self, 
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 db: Optional[int] = None,
                 password: Optional[str] = None,
                 max_connections: Optional[int] = None,
                 **kwargs):
        """
        Initialize Redis configuration.
        
        Args:
            host: Redis host (defaults to env var or localhost)
            port: Redis port (defaults to env var or 6379)
            db: Redis database number (defaults to env var or 0)
            password: Redis password (defaults to env var)
            max_connections: Maximum connections in pool
            **kwargs: Additional Redis connection parameters
        """
        self.host = host or os.getenv('REDIS_HOST', os.getenv('REDIS_SERVICE_HOST', 'localhost'))
        self.port = int(port or os.getenv('REDIS_PORT', os.getenv('REDIS_SERVICE_PORT', 6379)))
        self.db = int(db or os.getenv('REDIS_DB', 0))
        self.password = password or os.getenv('REDIS_PASSWORD')
        self.max_connections = int(max_connections or os.getenv('REDIS_MAX_CONNECTIONS', 20))
        
        # Additional connection parameters
        self.socket_timeout = kwargs.get('socket_timeout', 5)
        self.socket_connect_timeout = kwargs.get('socket_connect_timeout', 5)
        self.retry_on_timeout = kwargs.get('retry_on_timeout', True)
        self.health_check_interval = kwargs.get('health_check_interval', 30)
        
        # Connection pool for better performance
        self.pool = self._create_connection_pool()
        
        logger.info(f"Redis configured: {self.host}:{self.port}, DB: {self.db}, "
                   f"Max connections: {self.max_connections}")
    
    def _create_connection_pool(self) -> ConnectionPool:
        """Create Redis connection pool."""
        try:
            pool_kwargs = {
                'host': self.host,
                'port': self.port,
                'db': self.db,
                'max_connections': self.max_connections,
                'decode_responses': True,
                'socket_timeout': self.socket_timeout,
                'socket_connect_timeout': self.socket_connect_timeout,
                'retry_on_timeout': self.retry_on_timeout,
                'health_check_interval': self.health_check_interval
            }
            
            if self.password:
                pool_kwargs['password'] = self.password
            
            pool = ConnectionPool(**pool_kwargs)
            logger.info("Redis connection pool created successfully")
            return pool
            
        except Exception as e:
            logger.error(f"Failed to create Redis connection pool: {e}")
            raise
    
    def get_client(self) -> redis.Redis:
        """
        Get Redis client instance.
        
        Returns:
            Redis client using the connection pool
        """
        return redis.Redis(connection_pool=self.pool)
    
    def test_connection(self) -> bool:
        """
        Test Redis connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            client = self.get_client()
            client.ping()
            logger.info("Redis connection test successful")
            return True
        except Exception as e:
            logger.error(f"Redis connection test failed: {e}")
            return False
    
    def get_info(self) -> dict:
        """
        Get Redis server information.
        
        Returns:
            Dictionary with Redis server info
        """
        try:
            client = self.get_client()
            info = client.info()
            return {
                'redis_version': info.get('redis_version', 'unknown'),
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
        except Exception as e:
            logger.error(f"Failed to get Redis info: {e}")
            return {}
    
    def close(self):
        """Close connection pool."""
        try:
            if self.pool:
                self.pool.disconnect()
                logger.info("Redis connection pool closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection pool: {e}")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()

# Global Redis configuration instance
_redis_config: Optional[RedisConfig] = None

def get_redis_client(config: Optional[RedisConfig] = None) -> redis.Redis:
    """
    Get Redis client instance.
    
    Args:
        config: Optional RedisConfig instance
        
    Returns:
        Redis client
    """
    global _redis_config
    
    if config:
        return config.get_client()
    
    if _redis_config is None:
        _redis_config = RedisConfig()
    
    return _redis_config.get_client()

def configure_redis(**kwargs) -> RedisConfig:
    """
    Configure global Redis settings.
    
    Args:
        **kwargs: Redis configuration parameters
        
    Returns:
        RedisConfig instance
    """
    global _redis_config
    _redis_config = RedisConfig(**kwargs)
    return _redis_config

def test_redis_connection() -> bool:
    """
    Test Redis connection using global configuration.
    
    Returns:
        True if connection successful
    """
    try:
        client = get_redis_client()
        client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis connection test failed: {e}")
        return False
