import aiomysql
from typing import Optional, ClassVar
import asyncio

class DatabaseConnectionPool:
    _instance: Optional['DatabaseConnectionPool'] = None
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            raise RuntimeError("This class must be instantiated using 'await DatabaseConnectionPool.create()'")
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            raise RuntimeError("This class must be initialized using 'await DatabaseConnectionPool.create()'")

    @classmethod
    async def create(cls,**kwargs) -> 'DatabaseConnectionPool':
        async with cls._lock:
            if cls._instance is None:
                instance = super(DatabaseConnectionPool, cls).__new__(cls)
                await instance._async_init(**kwargs)
                cls._instance = instance
            return cls._instance

    async def _async_init(self,**kwargs):
        self.pool: aiomysql.Pool = await aiomysql.create_pool(**kwargs)
        self._initialized = True

    async def get_connection(self) -> aiomysql.Connection:
        """Asynchronously get a connection from the pool."""
        return await self.pool.acquire()

    async def execute_query(self, query: str, params=None):
        """
        Asynchronously execute a query using a connection from the pool.
        
        :param query: SQL query to execute.
        :param params: Optional parameters to pass with the query.
        """
        async with await self.get_connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()  # 获取所有结果


    async def execute_update(self, query: str, params=None):
        """
        Asynchronously execute an update or insert query.

        :param query: SQL query to execute.
        :param params: Optional parameters to pass with the query.
        """
        async with await self.get_connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query, params)
                await connection.commit()  # 提交更改
                return cursor.rowcount  # 返回影响的行数

    async def close_pool(self):
        """Close all connections in the pool."""
        self.pool.close()
        await self.pool.wait_closed()
        
    async def heartbeat(self):
        """Check the health of the pool and reconnect if necessary."""
        while True:
            try:
                async with self.pool.acquire() as connection:
                    await connection.ping()
                await asyncio.sleep(300)  # 如果ping成功，退出循环
            except (aiomysql.Error, asyncio.TimeoutError) as e:
                # 处理ping失败的情况
                print(f"Connection ping failed: {e}. Trying to reconnect...")
                await self.handle_connection_failure(connection)
                continue  # 尝试重新获取连接并ping

    async def handle_connection_failure(self, connection):
        """Close the failed connection and possibly log the event."""
        try:
            # 尝试关闭不健康的连接
            connection.close()
            await connection.wait_closed()
        except Exception as e:
            # 处理连接关闭失败的情况
            print(f"Failed to close unhealthy connection: {e}")