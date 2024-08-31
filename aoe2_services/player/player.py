from nonebot import on_command

from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot_plugin_waiter import prompt

from .process import (
    get_player_id_list,
    get_player_info_msg,
    get_candidate_msg
)
from ...AsyncDB import DatabaseConnectionPool


player_info = on_command("查询", priority=1)


@player_info.handle()
async def _(event: MessageEvent, arg=CommandArg()):
    arg = str(arg)
    player_id_list = await get_player_id_list(arg)
    if not player_id_list:
        await player_info.finish("没有找到该玩家")
    elif len(player_id_list) == 1:
        msg = await get_player_info_msg(player_id_list[0])
        await player_info.finish(msg if msg else "没有找到该玩家")
    else:
        resp = await prompt(await get_candidate_msg(player_id_list), timeout=60)
        if str(resp).isdigit():
            idx = int(str(resp))
            if idx >= 1 and idx <= len(player_id_list):
                await player_info.finish(
                    await get_player_info_msg(player_id_list[idx - 1])
                )


