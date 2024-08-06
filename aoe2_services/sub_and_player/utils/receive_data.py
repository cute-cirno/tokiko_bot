import asyncio
import json
import websockets
from nonebot.log import logger

async def websocket_client(uri: str, queue: asyncio.Queue, reconnect_interval=5):
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
            logger.info(f"Attempting to reconnect in {reconnect_interval} seconds...")
            await asyncio.sleep(reconnect_interval)  # 等待一段时间后重连
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            logger.info(f"Attempting to reconnect in {reconnect_interval} seconds...")
            await asyncio.sleep(reconnect_interval)  # 等待一段时间后重连