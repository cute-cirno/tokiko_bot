import asyncio
import json
import websockets
from collections import defaultdict
from typing import Any, Dict, List, Union

class WebSocketClient:
    def __init__(self, uri: str):
        self.uri = uri

    async def connect(self) -> None:
        async with websockets.connect(self.uri, max_size=1024 * 1024 * 10) as websocket:
            await websocket.send(json.dumps({"browser": True}))
            await asyncio.sleep(0.1)
            await websocket.send(json.dumps({"login": "undefined"}))
            await asyncio.sleep(0.1)
            await websocket.send(json.dumps({"focus": True}))

            while True:
                message = await websocket.recv()
                data: Dict[str, Any] = json.loads(message)
                if data:
                    await self.handle_message(data)

    async def handle_message(self, message: Dict[str, Any]) -> None:
        cls = int(message['cls'])
        if cls in (27,-1):
            self.print_cls_data(cls, message)
        if cls == 3:
            data_list = message.get('data', [])
            for data_item in data_list:
                if isinstance(data_item, dict):
                    item_cls = data_item.get('cls')
                    if item_cls:
                        await self.handle_message({'cls': item_cls, 'data': data_item})
    def print_cls_data(self, cls, data: Dict[str, Any]):
        print({f'{cls}': data})
        print()
        print()
    
async def main() -> None:
    uri = "wss://aoe2recs.com/dashboard/api/"
    WS = WebSocketClient(uri)
    await WS.connect()
    

if __name__ == "__main__":
    asyncio.run(main())