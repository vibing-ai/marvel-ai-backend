from redis.asyncio import Redis
from abc import ABC, abstractmethod
import os

# Abstract interface (SOLID - Interface Segregation)
class CacheInterface(ABC):
    @abstractmethod
    async def get(self, key: str): pass
    
    @abstractmethod
    async def set(self, key: str, value: str, ttl: int = None): pass

# Concrete implementation
class RedisService(CacheInterface):
    def __init__(self, redis_client: Redis = None):
        self.client = redis_client or Redis(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
    
    async def get(self, key: str):
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ttl: int = None):
        return await self.client.set(key, value, ex=ttl)
