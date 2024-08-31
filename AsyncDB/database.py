import asyncio
import aiomysql

from typing import cast
from nonebot.log import logger


class DatabaseConnectionPool:
    _instance: 'DatabaseConnectionPool | None' = None
    _lock: asyncio.Lock = asyncio.Lock()            # 初始化和重连加锁
    _pool_kwargs: dict
    _reconnecting: asyncio.Event = asyncio.Event()  # 用于标记是否正在重连

    def __new__(cls):
        if cls._instance:
            return cls._instance
        raise RuntimeError(
            "This class must be instantiated using 'await DatabaseConnectionPool.async_create()'")

    def __init__(self):
        if not hasattr(self, '_initialized'):
            raise RuntimeError(
                "This class must be initialized using 'await DatabaseConnectionPool.async_create()'")

    @classmethod
    async def async_create(cls, **kwargs) -> 'DatabaseConnectionPool':
        async with cls._lock:
            cls._pool_kwargs = kwargs
            if cls._instance is None:
                instance = super(DatabaseConnectionPool, cls).__new__(cls)
                await instance._async_init(**kwargs)
                cls._instance = instance
            return cls._instance

    async def _async_init(self):
        self._pool: aiomysql.Pool = await aiomysql.create_pool(**self._pool_kwargs)
        self._initialized = True
        asyncio.create_task(self.watchdog())

    async def _reconnect(self):
        """重新初始化连接池。"""
        async with self._lock:
            self._reconnecting.set()  # 设置正在重连标志
            try:
                if self._pool:
                    self._pool.close()
                    await self._pool.wait_closed()
                await self._async_init()
                logger.info("连接池重新初始化成功。")
            except Exception as e:
                logger.error(f"重新初始化连接池失败: {e}")
            finally:
                self._reconnecting.clear()  # 清除重连标志

    async def watchdog(self):
        """保持连接池的连接性。"""
        while True:
            try:
                async with self._pool.acquire() as connection:
                    await connection.ping()
                await asyncio.sleep(300)
            except (aiomysql.Error, asyncio.TimeoutError):
                await self._reconnect()
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                logger.info("心跳任务被取消")
                break
            except Exception as e:
                logger.error(f"心跳任务遇到错误: {e}")

    async def get_connection(self):
        """异步获取连接池中的一个连接。"""
        return await self._pool.acquire()


    async def get_cursor(self) -> tuple[aiomysql.Connection, aiomysql.DictCursor]:
        await self._reconnecting.wait()
        async with self._pool.acquire() as connection:
            connection = cast(aiomysql.Connection, connection)
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                cursor = cast(aiomysql.DictCursor, cursor)
                return connection, cursor

    async def execute_query(self, query: str, params=None) -> list[dict]:
        """异步执行查询语句并获取结果。"""
        _, cursor = await self.get_cursor()  # 只使用游标
        try:
            await cursor.execute(query, params)
            return await cursor.fetchall()
        finally:
            await cursor.close()

    async def execute_update(self, query: str, params=None) -> int:
        """异步执行数据变动语句。"""
        connection, cursor = await self.get_cursor()
        try:
            await cursor.execute(query, params)
            await connection.commit()  # 提交事务
            return cursor.rowcount
        finally:
            await cursor.close()
