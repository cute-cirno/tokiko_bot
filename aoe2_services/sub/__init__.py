from nonebot import on_command

from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import CommandArg
from nonebot_plugin_waiter import prompt

from .process import (
    get_player_by_id,
    submit_sub_player,
    cancle_sub_player_list,
    get_sub_player_msg,
    get_sub_player_list,
    submit_turn_sub,
    submit_turn_end
)

from ..common.process import get_player_id_list, get_candidate_msg

sub_player = on_command("订阅")
cancle_sub = on_command("取消订阅")
sub_list = on_command("订阅列表")
turn_sub = on_command("调整通知")
turn_end = on_command("调整狙击")


@sub_player.handle()
async def _(event: GroupMessageEvent, arg=CommandArg()):
    args = str(arg).split()
    name = args[0]
    player_id_list = await get_player_id_list(name)
    if not player_id_list:
        await sub_player.finish("没有找到该玩家")
    if len(player_id_list) == 1:
        player = await get_player_by_id(player_id_list[0])
        if not player:
            return
        if len(args) == 1:
            mark = player.name
        else:
            mark = args[1]
        success = await submit_sub_player(
            player.id, event.user_id, event.group_id, mark
        )
        if success:
            await sub_player.finish(
                f"订阅成功,未指定备注,备注为{mark}。使用以下指令可备注玩家：\n订阅 玩家 备注"
            )
    else:
        resp = await prompt(await get_candidate_msg(player_id_list), timeout=60)
        if not str(resp).isdigit():
            return
        idx = int(str(resp))
        if idx < 1 and idx > len(player_id_list):
            return
        player = await get_player_by_id(player_id_list[0])
        if not player:
            return
        if len(args) == 1:
            mark = player.name
        else:
            mark = args[1]
        success = await submit_sub_player(
            player.id, event.user_id, event.group_id, mark
        )
        if success:
            await sub_player.finish(
                f"订阅成功,未指定备注,备注为{mark}。使用以下指令可备注玩家：\n订阅 玩家 备注"
            )


@cancle_sub.handle()
async def _(event: GroupMessageEvent, arg=CommandArg()):
    args = str(arg)
    player_id_list = await get_player_id_list(args)
    success = await cancle_sub_player_list(
        player_id_list, event.user_id, event.group_id
    )
    if success > 0:
        await cancle_sub.finish(f"取消了{success}条订阅")
    else:
        await cancle_sub.finish("请检查输入参数")


@sub_list.handle()
async def _(event: GroupMessageEvent):
    await sub_list.finish(await get_sub_player_msg(event.user_id, event.group_id))


@turn_sub.handle()
async def _(event: GroupMessageEvent, arg=CommandArg()):
    args = str(arg).split()
    if not all(idx.isdigit() for idx in args):
        await turn_sub.finish("参数错误，应为空格分割的数字列表")
    sub_list = await get_sub_player_list(event.user_id, event.group_id)
    idx_list = list(map(int, set(args)))
    if not sub_list:
        await turn_sub.finish("订阅列表为空")
    if not all(1 <= idx <= len(sub_list) for idx in idx_list):
        await turn_sub.finish("参数错误，应为1-{}之间的数字".format(len(sub_list)))
    count = 0
    for idx in idx_list:
        count += await submit_turn_sub(sub_list[idx - 1][0], event.user_id, event.group_id)
    await turn_sub.finish(f"调整了{count}条通知")


@turn_end.handle()
async def _(event: GroupMessageEvent, arg=CommandArg()):
    args = str(arg).split()
    if not all(idx.isdigit() for idx in args):
        await turn_sub.finish("参数错误，应为空格分割的数字列表")
    sub_list = await get_sub_player_list(event.user_id, event.group_id)
    idx_list = list(map(int, set(args)))
    if not sub_list:
        await turn_sub.finish("订阅列表为空")
    if not all(1 <= idx <= len(sub_list) for idx in idx_list):
        await turn_sub.finish("参数错误，应为1-{}之间的数字".format(len(sub_list)))
    count = 0
    for idx in idx_list:
        count += await submit_turn_end(sub_list[idx - 1][0], event.user_id, event.group_id)
    await turn_sub.finish(f"调整了{count}条狙击")
