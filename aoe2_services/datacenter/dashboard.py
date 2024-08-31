import time

from .model.room import Room
from ..datacenter.sub_pusher import SubPusher


class RoomNotFoundError(Exception):
    pass


class DashBoard:
    def __init__(self) -> None:
        self._all_room: dict[int, Room] = {}
        self._whereis_player: dict[tuple[int, str], int] = {}

    def initialize(self):
        self._all_room.clear()
        self._whereis_player.clear()

    async def set_pusher(self, pusher: SubPusher):
        await pusher.init()
        self._sub_pusher: SubPusher = pusher

    def regist_player(self, room: Room):
        for player in room.players:
            if player.id == 0:
                continue
            self._whereis_player[(player.id, player.name)] = room.id

    def logoff_player(self, room: Room):
        for player in room.players:
            if player.id == 0:
                continue
            self._whereis_player.pop((player.id, player.name), None)

    def add_room(self, room_data: dict):
        room = Room(room_data)
        if room.id in self._all_room:
            self._remove_room(room)
        self._add_room(room)
        if hasattr(self, "_sub_pusher"):
            self._sub_pusher.check_add_room(room)

    def _add_room(self, room: Room):
        room.expired += 3600
        self._all_room[room.id] = room
        self.regist_player(room=room)

    def remove_room(self, room_id: int):
        room = self.get_room_by_id(room_id=room_id)
        if hasattr(self, "_sub_pusher"):
            self._sub_pusher.check_add_room(room)
        self._remove_room(room=room)

    def _remove_room(self, room: Room):
        if room.id in self._all_room:
            self.logoff_player(room)
            self._all_room.pop(room.id)

    def get_room(self, identifier: str) -> list[Room]:
        room_list: list[Room] = []

        identifier_lower = identifier.lower()
        isdigit_id = identifier.isdigit()

        for k, room_id in self._whereis_player.items():
            # 匹配整数 ID
            if isdigit_id and k[0] == int(identifier):
                room = self._all_room.get(room_id)
                if room:
                    room_list.append(room)
                continue

            # 匹配房间名称
            if identifier_lower in k[1].lower():
                room = self._all_room.get(room_id)
                if room:
                    room_list.append(room)

        # 如果房间列表为空，则抛出异常
        if not room_list:
            raise RoomNotFoundError(
                f'Room for identifier "{identifier}" not found')

        return room_list

    def get_room_by_id(self, room_id: int) -> Room:
        if room_id not in self._all_room:
            raise RoomNotFoundError(f'room {room_id} not found')
        return self._all_room[room_id]

    def remove_expired_room(self):
        now = int(time.time())
        for room in self._all_room.values():
            if now > room.expired:
                self._remove_room(room=room)

    @property
    def lobby_count(self) -> int:
        return sum(room.status == "lobby" for room in self._all_room.values())

    @property
    def ongoing_count(self) -> int:
        return sum(room.status == "ongoing" for room in self._all_room.values())
