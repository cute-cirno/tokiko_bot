import asyncio
import json
import websockets
from collections import defaultdict
from typing import Any, Dict, List, Union

class WebSocketClient:
    def __init__(self, uri: str, output_file: str):
        self.uri = uri
        self.output_file = output_file
        self.structures = self.read_from_file()

    def read_from_file(self) -> defaultdict:
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return defaultdict(dict, data)
        except (FileNotFoundError, json.JSONDecodeError):
            return defaultdict(dict)

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
        cls = message['cls']
        structure_changed = self.update_structure(cls, message)
        if cls == 3:
            data_list = message.get('data', [])
            for data_item in data_list:
                if isinstance(data_item, dict):
                    item_cls = data_item.get('cls')
                    if item_cls:
                        data = data_item.get('data', {})
                        structure_changed |= self.update_structure(item_cls, data)

        if structure_changed:
            self.write_to_file()
        print(f"Updated structure for cls {cls}: {self.structures[cls]}")

    def update_structure(self, cls: int, message: Dict[str, Any]) -> bool:
        structure_changed = False
        if isinstance(message, dict):
            for key, value in message.items():
                if key not in self.structures[cls]:
                    structure_changed = True
                    if isinstance(value, dict):
                        self.structures[cls][key] = self.infer_structure(value)
                    elif isinstance(value, list):
                        if value:
                            self.structures[cls][key] = [self.infer_structure(value[0])]
                        else:
                            self.structures[cls][key] = []
                    else:
                        self.structures[cls][key] = type(value).__name__
        return structure_changed

    def infer_structure(self, data: Union[Dict[str, Any], List[Any]]):
        if isinstance(data, dict):
            structure = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    structure[key] = self.infer_structure(value)
                elif isinstance(value, list):
                    if value:
                        structure[key] = [self.infer_structure(value[0])]
                    else:
                        structure[key] = []
                else:
                    structure[key] = type(value).__name__
            return structure
        elif isinstance(data, list) and data:
            return [self.infer_structure(data[0])]
        else:
            return {}

    def write_to_file(self) -> None:
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.structures, f, ensure_ascii=False, indent=4)

async def main() -> None:
    uri = "wss://aoe2recs.com/dashboard/api/"
    output_file = "structures.json"
    client = WebSocketClient(uri, output_file)
    await client.connect()

if __name__ == "__main__":
    asyncio.run(main())
