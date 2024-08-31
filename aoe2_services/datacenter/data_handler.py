import asyncio
import json
import websockets
from loguru import Logger


from .dashboard import DashBoard


class DataHandler:
    _instance = None
    _initialized = None

    def __new__(cls):
        if cls._instance:
            return cls._instance
        raise RuntimeError(
            "This class must be instantiated using 'await DataHandler.async_create()'")

    def __init__(self):
        if not hasattr(self, '_initialized'):
            raise RuntimeError(
                "This class must be initialized using 'await DataHandler.async_create()'")

    @classmethod
    async def async_create(cls, uri: str, logger: Logger) -> 'DataHandler':
        if cls._instance is None:
            instance = super(DataHandler, cls).__new__(cls)
            await instance._async_init(uri, logger)
            cls._instance = instance
        return cls._instance

    async def _async_init(self, uri: str, logger: Logger):
        self.logger = logger
        self.uri = uri
        self._message_queue = asyncio.Queue()
        self._dashboard = DashBoard()
        asyncio.create_task(self.websocket_client())
        asyncio.create_task(self.handle_messages())
        self._initialized = True

    async def websocket_client(self, reconnect_interval=5):
        uri = self.uri
        queue = self._message_queue
        logger = self.logger
        while True:
            try:
                # 尝试建立连接
                async with websockets.connect(uri, max_size=1024 * 1024 * 10) as websocket:
                    logger.info(f"Connected to {uri}")
                    await websocket.send(json.dumps({"browser": True}))
                    await asyncio.sleep(0.1)
                    await websocket.send(json.dumps({"login": "undefined"}))
                    await asyncio.sleep(0.1)
                    await websocket.send(json.dumps({"focus": True}))

                    # 处理消息
                    while True:
                        message = await websocket.recv()
                        logger.debug(f"Received message: {message}")
                        await queue.put(message)

            except websockets.exceptions.ConnectionClosed as e:
                logger.error(f"Connection closed: {e}")
                logger.info(
                    f"Attempting to reconnect in {reconnect_interval} seconds...")
                await asyncio.sleep(reconnect_interval)  # 等待一段时间后重连
            except Exception as e:
                logger.error(f"An error occurred: {e}")
                logger.info(
                    f"Attempting to reconnect in {reconnect_interval} seconds...")
                await asyncio.sleep(reconnect_interval)  # 等待一段时间后重连

    async def handle_messages(self):
        logger = self.logger
        while True:
            try:
                message = await self._message_queue.get()
                if message == "INITIALIZE":
                    self._dashboard.initialize()
                    continue
                data = json.loads(message)
                await self.process_message(data)
            except json.JSONDecodeError:
                logger.error(
                    "Failed to decode JSON from message: %s", message)
            except Exception as e:
                logger.error("An error occurred: %s", str(e))

    async def process_message(self, data: dict):
        data_cls = int(data.get("cls", 0))
        if data_cls == 0:
            return  # Ignore messages without a valid class

        target_id = int(data.get("target_id", 0))
        message_data = data.get("data", {})

        if data_cls in {27, 28}:
            if not message_data:
                self._dashboard.remove_room(target_id)
            else:
                self._dashboard.add_room(room_data=message_data)
        elif data_cls == 3:
            for sub_data in message_data:
                await self.process_message(sub_data)

    @property
    def lobby_count(self) -> int:
        return self._dashboard.lobby_count

    @property
    def ongoing_count(self) -> int:
        return self._dashboard.ongoing_count

    @property
    def dashboard(self) -> DashBoard:
        return self._dashboard
