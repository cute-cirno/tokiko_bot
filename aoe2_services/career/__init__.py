from .get_career import getCareerMsg
from nonebot.matcher import Matcher
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    MessageSegment
)
from nonebot_plugin_txt2img import Txt2Img
from nonebot.adapters import Message
from nonebot.params import CommandArg, ArgPlainText
from ..AsynOrm.models import Aoe2Player
from tortoise.expressions import Q
from ..utils.align_str import align_strings

career_info = on_command('帝国生涯', priority=5)


@career_info.handle()
async def _(matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    player_id = str(arg)
    if player_id.isdigit() and await check_id(player_id):
        message = await getCareerMsg(int(player_id))
        await push_msg(matcher, message)

    player_dict_list: list[dict] = await get_id_by_name(player_id)
    if len(player_dict_list) == 1:
        player_id = player_dict_list[0].get("player_id", 0)
        msg = await getCareerMsg(int(player_id))
        await push_msg(matcher, msg)
    elif len(player_dict_list) > 1:
        msg = '有多个相关玩家，请输入对应玩家序号：\n'
        msg_list = []
        for i, player_dict in enumerate(player_dict_list):
            msg_list.append(
                f'\n{i+1}. {player_dict["player_name"]} ({player_dict["rating_tg"]}/{player_dict["rating_1v1"]})'.split())
        msg_list = align_strings(msg_list)
        msg += str('\n'.join(msg_list))
        matcher.state['player_dict_list'] = player_dict_list
    else:
        msg = '没有找到相关玩家'
    await matcher.send(str(message))


@career_info.got('order')
async def _(matcher: Matcher, event: MessageEvent, order: str = ArgPlainText()):
    index = int(order) - 1
    player_id = matcher.state['player_dict_list'][index]["player_id"]
    msg = await getCareerMsg(int(player_id))
    if msg:
        font_size = 18
        text = msg
        Txt2Img().set_font_size(font_size)
        pic = Txt2Img().draw('', text)
        msg = MessageSegment.image(pic)
        await matcher.finish(msg)
    else:
        raise Exception('career msg is None')


# async def get_id_by_name(username: str) -> list[dict]:
#     db = DB()
#     sql = '''   SELECT player_id, player_name, rating_tg, rating_1v1
#                 FROM aoe2_player
#                 WHERE player_name LIKE %s
#                 ORDER BY LENGTH(LOWER(player_name)) ASC, rating_tg DESC
#                 LIMIT 9'''
#     if len(username) <= 2:
#         player_dict_list: list[dict] = await db.execute_query(query=sql, params=(f'{username}'))
#     elif len(username) <= 5:
#         player_dict_list: list[dict] = await db.execute_query(query=sql, params=(f'{username}'))
#     else:
#         player_dict_list: list[dict] = await db.execute_query(query=sql, params=(f'{username}'))
#     return player_dict_list


# async def check_id(player_id: str):
#     id = int(player_id)
#     query = "SELECT 1 FROM aoe2_player WHERE player_id = %s LIMIT 1"
#     db = DB()
#     result = await db.execute_query(query, (id,))
#     return len(result) == 1

async def get_id_by_name(username: str) -> list[dict]:
    query = Aoe2Player.filter(player_name__icontains=username)

    if len(username) <= 2:
        query = query.order_by("player_name", "-rating_tg")
    elif len(username) <= 5:
        query = query.order_by("player_name", "-rating_tg")
    else:
        query = query.order_by("player_name", "-rating_tg")

    # 获取最多9个玩家记录
    players = await query.limit(9).values("player_id", "player_name", "rating_tg", "rating_1v1")
    return players

async def check_id(player_id: str) -> bool:
    exists = await Aoe2Player.exists(Q(player_id=int(player_id)))
    return exists

async def push_msg(matcher: Matcher, msg):
    if msg:
        font_size = 18
        text = msg
        Txt2Img().set_font_size(font_size)
        pic = Txt2Img().draw('', text)
        message = MessageSegment.image(pic)
        await matcher.finish(message)
    else:
        raise Exception('career msg is None')
