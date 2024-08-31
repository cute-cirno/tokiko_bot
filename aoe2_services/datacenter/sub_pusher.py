from collections import defaultdict
from datetime import datetime
from abc import ABC, abstractmethod

from .model.sub import Sub
from .model.room import Room
from ...AsyncDB import DatabaseConnectionPool as DB

class SubPusher(ABC):
    _initialized = False

    def __init__(self) -> None:
        self._initialized = True
        self._need_push_start: set[int] = set()
        self._need_push_end: set[int] = set()
        self.sub_set: set[int] = set()
        self.sub_dict: dict[int, list[Sub]] = defaultdict(list)

    async def init(self):
        await self.load_sub()

    def get_group_push(self, need_push_set: set) -> dict[int, list[Sub]]:
        group_push: dict[int, list[Sub]] = defaultdict(list)
        for sub_id in need_push_set:
            for sub in self.sub_dict[sub_id]:
                if not sub.isexpire():
                    group_push[sub.group_id].append(sub)
                else:
                    self.sub_dict[sub_id].remove(sub)
        return group_push

    async def push(self):
        start_group_push = self.get_group_push(self._need_push_start)
        for group_id, group_sub_list, in start_group_push.items():
            info = await self.get_push_info(
                group_sub_list=group_sub_list, type="start")
            await self._push(group_id, info)

        end_group_push = self.get_group_push(self._need_push_end)
        for group_id, group_sub_list, in end_group_push.items():
            info = await self.get_push_info(
                group_sub_list=group_sub_list, type="end")
            await self._push(group_id, info)

    @abstractmethod
    async def _push(self, group_id: int, push_info: dict):
        """需要实现往群里发消息"""
        raise NotImplementedError

    @abstractmethod
    async def get_name_nickname_info(self, player_info: dict[int, list[str]]) -> dict[str, list[str]]:
        """实现把传入的玩家id(int)转为玩家昵称"""
        raise NotImplementedError

    async def get_push_info(self, group_sub_list: list[Sub], type: str) -> dict:
        info = {}
        at_set: set[int] = set()
        player_info: dict[int, list[str]] = {}
        for sub in group_sub_list:
            at_set.add(sub.qq_id)
            player_info[sub.player_id].append(sub.nickname)
        info["at_set"] = at_set
        info["player_info"] = await self.get_name_nickname_info(player_info)
        info["type"] = type
        return info

    async def load_sub(self):
        db = DB()  # Ensure DB is properly defined and initialized
        sql = """
            SELECT
                player_id, qq_id, group_id, sub, end, mark, create_time
            FROM
                aoe2_fan
        """
        try:
            sub_info_list = await db.execute_query(sql)
        except Exception as e:
            # Log or handle the exception
            raise Exception
        else:
            for sub_info in sub_info_list:
                player_id: int = sub_info['player_id']
                self.sub_set.add(player_id)
                sub = Sub(**sub_info)
                self.sub_dict[player_id].append(sub)

    def sub_change_handler(self):
        pass

    def check_add_room(self, room: Room):
        need_push = self.sub_set & room.player_set
        self._need_push_start.update(need_push)

    def check_remove_room(self, room: Room):
        need_push = self.sub_set & room.player_set
        self._need_push_end.update(need_push)

    def add_sub(self, player_id: int, group_id: int, qq_id: int, nickname: str, create_time: datetime, priority=10):
        sub = Sub()
        sub.player_id = player_id
        sub.group_id = group_id
        sub.qq_id = qq_id
        sub.nickname = nickname
        sub.create_time = create_time
        sub.priority = priority
        self.sub_set.add(player_id)
        self.sub_dict[player_id].append(sub)

    def remove_sub(self, player_id: int, group_id: int, qq_id: int):
        self._remove_sub(player_id=player_id, group_id=group_id, qq_id=qq_id)

    def _remove_sub(self, player_id: int, group_id: int, qq_id: int) -> Sub:
        for sub in self.sub_dict[player_id]:
            if sub.qq_id == qq_id and sub.group_id == group_id:
                self.sub_dict[player_id].remove(sub)

        if not self.sub_dict[player_id]:
            self.sub_dict.pop(player_id)
            self.sub_set.remove(player_id)
        raise Exception("未找到该订阅")
