from .get_career import getCareerMsg
from nonebot.matcher import Matcher
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    MessageSegment
)
from nonebot_plugin_txt2img import Txt2Img
from nonebot.adapters import Message
from nonebot.params import CommandArg,ArgPlainText
from ...AsyncDB import DatabaseConnectionPool as DB
from .align_str import align_strings

career_info = on_command('帝国生涯', priority=5)

@career_info.handle()
async def _(matcher:Matcher, event:MessageEvent, arg: Message = CommandArg()):
    player_id = str(arg)
    if player_id.isdigit() and await check_id(player_id):
        message = await getCareerMsg(int(player_id))
        await push_msg(matcher,message)
        
        
    player_list = await get_id_by_name(player_id)
    if len(player_list)==1:
        player_id = player_list[0][0]
        msg = await getCareerMsg(int(player_id))
        await push_msg(matcher,msg)
    elif len(player_list)>1:
        msg = '有多个相关玩家，请输入对应玩家序号：\n'
        msg_list = []
        for i, player in enumerate(player_list):
            msg_list.append(f'\n{i+1}. {player[1]} ({player[3]}/{player[2]})')
        msg_list = align_strings(msg_list)
        msg += str('\n'.join(msg_list))
        matcher.state['player_list'] = player_list
    else:
        msg = '没有找到相关玩家'
    await matcher.send(str(message))
    
@career_info.got('order')
async def _(matcher:Matcher, event:MessageEvent, order:str = ArgPlainText()):
    index = int(order) - 1
    player_id = matcher.state['player_list'][index][0]
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
        
async def get_id_by_name(username:str):
    db = DB()
    sql = '''   SELECT player_id, player_name, rating_tg, rating_1v1
                FROM aoe2_player
                WHERE player_name LIKE %s
                ORDER BY LENGTH(LOWER(player_name)) ASC, rating_tg DESC
                LIMIT 9'''
    if len(username) <= 2:
        player_tuples = await db.execute_query(query=sql,params=(f'{username}'))
    elif len(username) <= 5:
        player_tuples = await db.execute_query(sql,(f'%{username}%'))
    else:
        player_tuples = await db.execute_query(sql,(f'{username}%'))
    return player_tuples
    
async def check_id(player_id:str):
    id = int(player_id)
    query = "SELECT 1 FROM aoe2_player WHERE player_id = %s LIMIT 1"
    db = DB()
    result = await db.execute_query(query, (id,))
    return len(result) == 1

async def push_msg(matcher:Matcher,msg):
    if msg:
        font_size = 18
        text = msg
        Txt2Img().set_font_size(font_size)
        pic = Txt2Img().draw('', text)
        message = MessageSegment.image(pic)
        await matcher.finish(message)
    else:
        raise Exception('career msg is None')