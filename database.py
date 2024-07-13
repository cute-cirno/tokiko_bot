import aiomysql
from asyncio import Lock, get_event_loop

class AsyncDatabaseConnectionPool:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            raise Exception("This class must be initialized using 'await AsyncDatabaseConnectionPool.create_instance()'")
        return cls._instance
    
    @classmethod
    async def create_instance(cls):
        async with cls._lock:
            if cls._instance is None:
                self = super().__new__(cls)
                self.pool = await aiomysql.create_pool(host='',port=0,
                                                       user='root',password='',
                                                       db='',minsize=2,maxsize=10)
                cls._instance = self
            return cls._instance
    
    async def get_connection(self):
        return await self.pool.acquire()
    
    async def release_connection(self,connection):
        self.pool.release(connection)
        
    async def close_pool(self):
        self.pool.close()
        await self.pool.wait_closed()