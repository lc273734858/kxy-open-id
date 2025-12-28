import redis.asyncio as redis
import uuid
from typing import Optional
from app.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB


class RedisClient:
    _instance = None

    @classmethod
    async def get_instance(cls)->redis.Redis:
        if cls._instance is None:
            cls._instance = await redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD if REDIS_PASSWORD else None,
                db=REDIS_DB,
                decode_responses=True
            )
        return cls._instance

    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None

    @classmethod
    async def acquire_lock(cls, lock_key: str, timeout: int = 10) -> Optional[str]:
        """
        获取分布式锁

        Args:
            lock_key: 锁的键名
            timeout: 锁的超时时间（秒），防止死锁

        Returns:
            str: 锁的唯一标识（用于释放锁时验证），获取失败返回 None
        """
        redis_client = await cls.get_instance()
        lock_value = str(uuid.uuid4())

        # SET NX EX: 仅在键不存在时设置，并设置过期时间
        acquired = await redis_client.set(lock_key, lock_value, nx=True, ex=timeout)

        return lock_value if acquired else None

    @classmethod
    async def release_lock(cls, lock_key: str, lock_value: str) -> bool:
        """
        释放分布式锁（使用Lua脚本保证原子性）

        Args:
            lock_key: 锁的键名
            lock_value: 锁的唯一标识（防止误删其他进程的锁）

        Returns:
            bool: 是否成功释放锁
        """
        redis_client = await cls.get_instance()

        # Lua脚本：仅当值匹配时才删除锁（防止误删其他进程的锁）
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """

        result = await redis_client.eval(lua_script, 1, lock_key, lock_value)
        return result == 1
