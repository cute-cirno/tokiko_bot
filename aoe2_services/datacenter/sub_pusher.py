from collections import defaultdict
from datetime import datetime
from abc import ABC, abstractmethod

import nonebot
from nonebot.adapters.onebot.v11 import MessageSegment

from .model.sub import Sub
from .model.room import Room
from ..AsynOrm.models import Aoe2Fan, Aoe2Player

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
                if not sub.expired:
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

    async def _push(self, group_id: int, push_info: dict):
        at_msg_list = [MessageSegment.at(qq_id)
                       for qq_id in push_info.get("at_set", set())]
        bot = nonebot.get_bot()
        await bot.call_api('send_group_msg', **{'group_id': group_id, 'message': push_info})



    async def get_push_info(self, group_sub_list: list[Sub], type: str) -> dict:
        info = {}
        at_set: set[int] = set()
        player_info: dict[str, list[str]] = {}
        for sub in group_sub_list:
            p = await Aoe2Player.get(player_id=sub.player_id)
            at_set.add(sub.qq_id)
            player_info[p.player_name].append(sub.nickname)
        info["at_set"] = at_set
        info["player_info"] = player_info
        info["type"] = type
        return info

    async def load_sub(self):
        try:
            # 查询所有记录并提取字段值
            sub_info_list = await Aoe2Fan.all().values(
                'player_id', 'qq_id', 'group_id', 'sub', 'end', 'mark', 'create_time'
            )
            
            # 处理查询结果
            for sub_info in sub_info_list:
                player_id = sub_info['player_id']
                self.sub_set.add(player_id)
                
                # 创建 Sub 实例并添加到字典
                sub = Sub(**sub_info)
                
                if player_id not in self.sub_dict:
                    self.sub_dict[player_id] = []
                    
                self.sub_dict[player_id].append(sub)

        except Exception as e:
            # 记录或处理异常
            raise Exception("Failed to load sub data")

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
