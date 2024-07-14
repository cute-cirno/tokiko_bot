import aiomysql
import asyncio

class MySQLPool:
    _instance = None
    _lock = asyncio.Lock()
    _initialized = False
    _running = True

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MySQLPool, cls).__new__(cls)
        return cls._instance

    async def _init_pool(self, host, port, user, password, db, minsize=2, maxsize=10, **kwargs):
        self.pool = await aiomysql.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
            minsize=minsize,
            maxsize=maxsize,
            **kwargs
        )
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self._initialized = True

    @classmethod
    async def create_instance(cls, **kwargs):
        async with cls._lock:
            if cls._instance is None:
                self = cls()
                await self._init_pool(**kwargs)
                cls._instance = self
            elif not cls._instance._initialized:
                await cls._instance._init_pool(**kwargs)
            return cls._instance

    async def acquire_connection(self):
        while True:
            conn = await self.pool.acquire()
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1;")
                    result = await cursor.fetchone()
                    if result:
                        return conn
                    else:
                        raise aiomysql.OperationalError("Connection is invalid")
            except aiomysql.OperationalError:
                print("Connection is invalid, trying to acquire a new connection...")
                self.pool.release(conn)  # 释放无效连接
                await asyncio.sleep(1)  # 短暂等待后重试

    async def execute_query(self, query, params=None):
        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                conn = await self.acquire_connection()
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    result = await cursor.fetchall()
                    self.pool.release(conn)  # 释放连接回池
                    return result
            except (aiomysql.MySQLError, aiomysql.OperationalError) as e:
                if attempt < retry_attempts - 1:
                    print(f"Query failed, retrying... (attempt {attempt + 1})")
                    await asyncio.sleep(1)  # 短暂等待后重试
                else:
                    print(f"Query failed after {retry_attempts} attempts: {e}")
                    raise

    async def heart_beat(self):
            while self._running:
                async with self.pool.acquire() as conn:
                    try:
                        async with conn.cursor() as cursor:
                            await cursor.execute("SELECT 1;")
                            await cursor.fetchone()
                    except aiomysql.OperationalError:
                        # 处理错误并移除失效连接
                        print("Detected invalid connection, removing from pool...")
                        self.pool._free.remove(conn)
                        conn.close()
                        await self.pool._fill_free_pool(True)  # 补充新的连接
                await asyncio.sleep(60)  # 设置适当的心跳间隔时间

    def close(self):
        self._running = False
        if self.pool:
            self.pool.close()
