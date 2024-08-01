import asyncio
import json
import websockets
from nonebot.log import logger

async def websocket_client(uri: str, queue: asyncio.Queue):
    async with websockets.connect(uri, max_size=1024 * 1024 * 10) as websocket:
        logger.info(f"Connected to {uri}")
        await websocket.send(json.dumps({"browser": True}))
        await asyncio.sleep(0.1)
        await websocket.send(json.dumps({"login": "undefined"}))
        await asyncio.sleep(0.1)
        await websocket.send(json.dumps({"focus": True}))    
        while True:
            message = await websocket.recv()
            logger.info(f"Received message: {message}")
            await queue.put(message)