import aiomysql
from typing import Optional, ClassVar
import asyncio
from nonebot.log import logger

class DatabaseConnectionPool:
    _instance: Optional['DatabaseConnectionPool'] = None
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            raise RuntimeError("This class must be instantiated using 'await DatabaseConnectionPool.async_create()'")
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            raise RuntimeError("This class must be initialized using 'await DatabaseConnectionPool.async_create()'")

    @classmethod
    async def async_create(cls, **kwargs) -> 'DatabaseConnectionPool':
        async with cls._lock:
            if cls._instance is None:
                instance = super(DatabaseConnectionPool, cls).__new__(cls)
                await instance._async_init(**kwargs)
                cls._instance = instance
            return cls._instance

    async def _async_init(self, **kwargs):
        self.pool: aiomysql.Pool = await aiomysql.create_pool(**kwargs)
        self._initialized = True
        asyncio.create_task(self.start_heartbeat())

    async def start_heartbeat(self):
        """Start a heartbeat task to maintain pool connectivity."""
        while True:
            try:
                async with self.pool.acquire() as connection:
                    await connection.ping()
                await asyncio.sleep(300)
            except (aiomysql.Error, asyncio.TimeoutError) as e:
                logger.error(f"Connection ping failed: {e}. Trying to reconnect...")
                await self.handle_connection_failure(connection)
                continue

    async def get_connection(self) -> aiomysql.Connection:
        """Asynchronously get a connection from the pool."""
        return await self.pool.acquire()

    async def execute_query(self, query: str, params=None) -> list[tuple]:
        """Asynchronously execute a query using a connection from the pool."""
        async with await self.get_connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()

    async def execute_update(self, query: str, params=None):
        """Asynchronously execute an update or insert query."""
        async with await self.get_connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query, params)
                await connection.commit()
                return cursor.rowcount

    async def close_pool(self):
        """Close all connections in the pool."""
        self.pool.close()
        await self.pool.wait_closed()

    async def handle_connection_failure(self, connection):
        """Close the failed connection and possibly log the event."""
        try:
            connection.close()
            await connection.wait_closed()
        except Exception as e:
            logger.error(f"Failed to close unhealthy connection: {e}")
