import asyncio
import json
from nonebot.log import logger as logging

from typing import Dict, Any, Union, Optional

from .receive_data import websocket_client
from ..model import Lobby, Ongoing, OngoingModel, LobbyModel


class DataHandler:
    _instance = None

    def __new__(cls, uri=str):
        if cls._instance is None:
            cls._instance = super(DataHandler, cls).__new__(cls)
        return cls._instance
    
    async def start(self, uri: str):
        # 启动 WebSocket 客户端，并将消息队列传递给它
        self.uri = uri
        self._message_queue = asyncio.Queue()
        self._lobby = Lobby()
        self._ongoing = Ongoing()
        asyncio.create_task(websocket_client(self.uri, self._message_queue))
        asyncio.create_task(self.handle_messages())

    async def handle_messages(self):
        while True:
            try:
                message = await self._message_queue.get()
                data = json.loads(message)
                await self.process_message(data)
            except json.JSONDecodeError:
                logging.error("Failed to decode JSON from message: %s", message)
            except Exception as e:
                logging.error("An error occurred: %s", str(e))

    async def process_message(self, data: Dict[str, Any]):
        data_cls = int(data.get("cls", 0))
        if data_cls == 0:
            return  # Ignore messages without a valid class

        target_id = data.get("target_id", 0)
        message_data = data.get("data", {})

        if data_cls == 27:
            if not message_data:
                self._ongoing.remove_room(target_id)
            else:
                ongoing_room = OngoingModel(message_data)
                self._ongoing.add_room(ongoing_room)
        elif data_cls == 28:
            if not message_data:
                self._lobby.remove_room(target_id)
            else:
                lobby_room = LobbyModel(message_data)
                self._lobby.add_room(lobby_room)
        elif data_cls == 3:
            for sub_data in message_data:
                await self.process_message(sub_data)


    async def get_lobby(self):
        return self._lobby

    async def get_room(self, identifier: Union[int, str])->Union[LobbyModel, OngoingModel, None]:
        return self._ongoing.get_room(identifier) or self._lobby.get_room(identifier)
    
    @property
    def room_count(self)->tuple:
        return (self._lobby.room_count, self._ongoing.room_count)
