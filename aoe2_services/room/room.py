from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg, ArgPlainText

from .process import check_player_and_get_room, get_all_room_msg, room2msg, candidate_msg
from ..datacenter.dashboard import RoomNotFoundError

spect_player = on_command("查房")
all_room = on_command("有多少房间")


@spect_player.handle()
async def _(event: MessageEvent, matcher: Matcher, args=CommandArg()):
    args = str(args).strip()
    try:
        room_list = check_player_and_get_room(args)
    except RoomNotFoundError:
        await spect_player.finish("没有找到房间")
    if len(room_list) == 1:
        msg = room2msg(room_list[0])
        await spect_player.finish(msg if msg else "没有找到房间")
    else:
        msg = candidate_msg(room_list)
        matcher.state['room_list'] = room_list
        await spect_player.send(msg)
    
    
@spect_player.got("order", prompt="请选择房间序号")
async def _(matcher:Matcher, event:MessageEvent, order:str = ArgPlainText()):
    if not order.isdigit():
        await spect_player.finish("错误序号，退出选择")
    index = int(order) - 1
    if index < 1 or index >= len(matcher.state['room_list']):
        await spect_player.finish("错误序号，退出选择")
    await spect_player.finish(room2msg(matcher.state['room_list'][index]))
        
        
@all_room.handle()
async def _(event: MessageEvent):
    msg = get_all_room_msg()
    if msg:
        await all_room.finish(msg)
    else:
        await all_room.finish("error")


# query = on_command('查询玩家',aliases={'查询id','查询ID','查id'}, priority=5)
# sub_list_query = on_command('订阅列表',aliases={'订阅名单','监视名单','监视列表'}, priority=5)
# end_list_query = on_command('狙击列表',aliases={'狙击名单'}, priority=5)
# cancle_sub = on_command('取消订阅',aliases={'释放'}, priority=5)
# cancle_end = on_command('取消狙击', priority=5)
# get_by_id = on_command('查房',aliases={'视奸'}, priority=5)
# spec = on_command('观战',aliases={'link'}, priority=5)
# end = on_command('狙击', priority=5)
# get_ongoing_num = on_command('有多少对局',aliases={'对局数量'}, priority=5)
# get_lobby_num = on_command('有多少房间',aliases={'房间数量'}, priority=5)

# @get_by_id.handle()
# async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
#     release = (False,None)
#     player_name = str(args).strip().lower()
#     ongoing = copy.copy(nonebot.get_driver().config.ongoing)
#     msg = ''
#     wrongRoomIDList = []
#     for k,v in ongoing.items():
#         players = v['players'] if 'players' in v else None
#         player_name_list = [_['name'].lower() if 'name' in _ else 'AI' for _ in players]
#         if player_name in player_name_list:
#             rms = v['rms'] if 'rms' in v else None
#             diplomacy = v['diplomacy'] if 'diplomacy' in v else None
#             average_rating = v['average_rating']
#             players = v['players'] if 'players' in v else None
#             player_list_sort_by_team = [_['members'] for _ in v['teams']] if 'teams' in v else None

#             color_list = [None,'blue','red','green','yellow','aqua','purple','grey','orange']

#             from wcwidth import wcswidth
#             # 确定每个字段的最大显示宽度
#             max_name_length = max(wcswidth(p['name']) for p in players if 'ai' not in p)
#             max_color_length = max(len(color_list[p['color']]) for p in players if p['color'] is not None)
#             max_civ_length = max(len(p['civilization']) for p in players)

#             player_info = ''
#             if player_list_sort_by_team and players:
#                 current_time = datetime.now().timestamp() #检查超时
#                 past_time = int(v['lobby_created'] if v['lobby_created'] else 0)
#                 time_difference = current_time - past_time
#                 if time_difference // 3600 >= 2:
#                     release = True
#                     wrongRoomIDList.append(k)
#                     continue

#                 if player_list_sort_by_team and players:
#                     for l in player_list_sort_by_team:
#                         for n in l:
#                             for p in players:
#                                 if p['number'] == n:
#                                     name = p['name'] if 'ai' not in p else 'AI'
#                                     color = color_list[p['color']]
#                                     civ = p['civilization']
#                                     rating_1v1 = p['rating_1v1'] if 'rating_1v1' in p else 'N/A'
#                                     rating_tg = p['rating_tg'] if 'rating_tg' in p else 'N/A'
#                                     # 使用 wcswidth 调整字符串宽度
#                                     player_info += f"{name: <{max_name_length - (wcswidth(name) - len(name))}}  {color:<{max_color_length}} {civ:<{max_civ_length}} ({rating_1v1:<4}/{rating_tg:<4})\n"
#             spectating_delay = v['spectating_delay'] if 'spectating_delay' in v else 0
#             link = v['link'] if 'link' in v else None
#             msg = f"ID:{k}\nMap:{rms}\nStart at:{time_ago(v['lobby_created'])}\nTeam mode:{diplomacy}\nAverage_rating:{average_rating}\nPlayers:\n\n{player_info}\nSpectating delay:{spectating_delay}"
#             font_size = 18
#             text = msg
#             Txt2Img().set_font_size(font_size)
#             pic = Txt2Img().draw('', text)
#             msg = MessageSegment.image(pic)
#             await matcher.send(link+msg)
#     if release:
#         [nonebot.get_driver().config.ongoing.pop(k) for k in wrongRoomIDList]
#     if not msg:
#         await matcher.finish('该玩家没有在进行的对局')


# def time_ago(timestamp):
#     current_time = datetime.now()
#     past_time = datetime.fromtimestamp(timestamp)

#     time_difference = current_time - past_time

#     if time_difference.days > 365:
#         return f"{time_difference.days // 365} years ago"
#     elif time_difference.days > 30:
#         return f"{time_difference.days // 30} months ago"
#     elif time_difference.days > 0:
#         return f"{time_difference.days} days ago"
#     elif time_difference.seconds // 3600 > 0:
#         return f"{time_difference.seconds // 3600} hours ago"
#     elif time_difference.seconds // 60 > 0:
#         return f"{time_difference.seconds // 60} minutes ago"
#     else:
#         return "Just now"


# @get_ongoing_num.handle()
# async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
#     ongoing = copy.copy(nonebot.get_driver().config.ongoing)
#     await matcher.finish(str(len(ongoing)))

# @get_lobby_num.handle()
# async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
#     lobby = copy.copy(nonebot.get_driver().config.lobby)
#     await matcher.finish(str(len(lobby)))


# @spec.handle()
# async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
#     player_name = str(args).strip().lower()
#     ongoing = copy.copy(nonebot.get_driver().config.ongoing)
#     link = ''
#     for k,v in ongoing.items():
#         players = v['players'] if 'players' in v else None
#         player_name_list = [_['name'].lower() if 'name' in _ else 'AI' for _ in players]
#         if player_name in player_name_list:
#             link = v['link'] if 'link' in v else None
#             await matcher.send(link)
#     if not link:
#         await matcher.finish('该玩家没有在进行的对局')

# @end.handle()
# async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
#     id = str(args).strip()
#     if not id.isdigit():
#         await matcher.finish('请保证id为纯数字')

#     id = int(id)
#     if id == 5760937:
#         await matcher.finish('不许狙击主人')
#     DB = nonebot.get_driver().config.DB
#     sql = '''SELECT * FROM aoe2_player WHERE player_id = %s'''
#     player_tuples = DB.execute_sqlP(sql,(id))
#     if len(player_tuples) == 0:
#         await matcher.finish('id不存在或者尚未录入')
#     else:
#         try:
#             DB.startTransaction()
#             group_id = event.group_id
#             user_id = event.user_id
#             sql_query = 'select follower_id_list from aoe2_end where group_id = %s and subscribe_id = %s'
#             follower_id_list = DB.execute_sqlP(sql_query,(group_id,id))
#             if len(follower_id_list)>0:
#                 info = json.loads(follower_id_list[0]['follower_id_list'])
#                 id_list = info['id_list']
#                 if user_id in id_list:
#                     await matcher.finish('该玩家已存在于你的狙击套餐中')
#                 id_list.append(user_id)
#                 info['id_list'] = id_list
#                 sql = '''update aoe2_end set follower_id_list = %s where group_id = %s and subscribe_id = %s'''
#                 DB.ExecuteNonQueryP(sql,
#                                     (json.dumps(info),
#                                     group_id,
#                                     id
#                                     )
#                 )
#             else:
#                 sql = '''insert into aoe2_end (group_id,subscribe_id,follower_id_list) values (%s,%s,%s)'''
#                 f = {}
#                 f['id_list'] = [user_id]
#                 DB.ExecuteNonQueryP(sql,
#                                     (group_id,
#                                     id,
#                                     json.dumps(f))
#                 )
#             DB.commit()
#             await matcher.finish(f"正在等待狙击{player_tuples[0]['player_name']}")
#         except FinishedException:
#             pass
#         except Exception as e:
#             DB.rollback()
#             await matcher.finish(f'{e}')

# @sub.handle()
# async def _(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
#     id = str(args).strip()
#     if not id.isdigit():
#         # await matcher.finish('请保证id为纯数字')
#         return

#     id = int(id)
#     DB = nonebot.get_driver().config.DB
#     sql = '''SELECT * FROM aoe2_player WHERE player_id = %s'''
#     player_tuples = DB.execute_sqlP(sql,(id))
#     if len(player_tuples) == 0:
#         await matcher.finish('id不存在或者尚未录入')
#     else:
#         try:
#             DB.startTransaction()
#             group_id = event.group_id
#             user_id = event.user_id
#             sql_query = 'select follower_id_list from aoe2_sub where group_id = %s and subscribe_id = %s'
#             follower_id_list = DB.execute_sqlP(sql_query,(group_id,id))
#             if len(follower_id_list)>0:
#                 info = json.loads(follower_id_list[0]['follower_id_list'])
#                 id_list = info['id_list']
#                 if user_id in id_list:
#                     await matcher.finish('你已关注此玩家')
#                 id_list.append(user_id)
#                 info['id_list'] = id_list
#                 sql = '''update aoe2_sub set follower_id_list = %s where group_id = %s and subscribe_id = %s'''
#                 DB.ExecuteNonQueryP(sql,
#                                     (json.dumps(info),
#                                     group_id,
#                                     id
#                                     )
#                 )
#             else:
#                 sql = '''insert into aoe2_sub (group_id,subscribe_id,follower_id_list) values (%s,%s,%s)'''
#                 f = {}
#                 f['id_list'] = [user_id]
#                 DB.ExecuteNonQueryP(sql,
#                                     (group_id,
#                                     id,
#                                     json.dumps(f))
#                 )
#             DB.commit()
#             await matcher.finish(f"已成功订阅{player_tuples[0]['player_name']}")
#         except FinishedException:
#             pass
#         except Exception as e:
#             DB.rollback()
#             await matcher.finish(f'{e}')

# @cancle_sub.handle()
# async def _(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
#     id = str(args).strip()
#     group_id = event.group_id
#     user_id = event.user_id
#     if not id.isdigit():
#     #    await matcher.finish('请保证id为纯数字')
#         return

#     id = int(id)
#     DB = nonebot.get_driver().config.DB
#     sql = '''SELECT follower_id_list FROM aoe2_sub WHERE subscribe_id = %s and group_id = %s'''
#     result = DB.execute_sqlP(sql,(id,group_id))
#     follower_id_list = json.loads(result[0]['follower_id_list']) if len(result) > 0 else {}
#     if user_id not in follower_id_list['id_list']:
#         await matcher.finish('你尚未订阅该玩家')
#     follower_id_list['id_list'].remove(user_id)
#     sql = '''update aoe2_sub set follower_id_list = %s where subscribe_id = %s and group_id = %s'''
#     DB.startTransaction()
#     try:
#         DB.ExecuteNonQueryP(sql,
#                             (
#                                 json.dumps(follower_id_list),
#                                 id,
#                                 group_id,
#                             )
#                             )
#         DB.commit()
#         await matcher.finish('取消成功')
#     except FinishedException:
#         pass
#     except Exception as e:
#         DB.rollback()
#         await matcher.finish(f'{e}')


# @cancle_end.handle()
# async def _(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
#     id = str(args).strip()
#     group_id = event.group_id
#     user_id = event.user_id
#     if not id.isdigit():
#         await matcher.finish('请保证id为纯数字')

#     id = int(id)
#     DB = nonebot.get_driver().config.DB
#     sql = '''SELECT follower_id_list FROM aoe2_end WHERE subscribe_id = %s and group_id = %s'''
#     result = DB.execute_sqlP(sql,(id,group_id))
#     follower_id_list = json.loads(result[0]['follower_id_list']) if len(result) > 0 else {}
#     if user_id not in follower_id_list['id_list']:
#         await matcher.finish('你尚未狙击该玩家')
#     follower_id_list['id_list'].remove(user_id)
#     sql = '''update aoe2_end set follower_id_list = %s where subscribe_id = %s and group_id = %s'''
#     DB.startTransaction()
#     try:
#         DB.ExecuteNonQueryP(sql,
#                             (
#                                 json.dumps(follower_id_list),
#                                 id,
#                                 group_id,
#                             )
#                             )
#         DB.commit()
#         await matcher.finish('取消成功')
#     except FinishedException:
#         pass
#     except Exception as e:
#         DB.rollback()
#         await matcher.finish(f'{e}')


# @sub_list_query.handle()
# async def _(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
#     group_id = event.group_id
#     user_id = event.user_id
#     DB = nonebot.get_driver().config.DB
#     sql =   '''
#             SELECT
#                 aoe2_sub.subscribe_id,
#                 aoe2_sub.follower_id_list,
#                 aoe2_player.player_name,
#                 aoe2_sub.group_id
#             FROM
#                 aoe2_sub
#             INNER JOIN
#                 aoe2_player ON aoe2_sub.subscribe_id = aoe2_player.player_id AND group_id = %s
#             '''
#     subscribe_info = DB.execute_sqlP(sql,(group_id))
#     msg = '你订阅的id列表如下'
#     for sub in subscribe_info:
#         follower_id_list = json.loads(sub['follower_id_list'])
#         if user_id in follower_id_list['id_list']:
#             msg += '\n' + str(sub['subscribe_id']) + '·' + sub['player_name']
#     await matcher.finish(msg)


# @end_list_query.handle()
# async def _(matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
#     group_id = event.group_id
#     user_id = event.user_id
#     DB = nonebot.get_driver().config.DB
#     sql =   '''
#             SELECT
#                 aoe2_end.subscribe_id,
#                 aoe2_end.follower_id_list,
#                 aoe2_player.player_name,
#                 aoe2_end.group_id
#             FROM
#                 aoe2_end
#             INNER JOIN
#                 aoe2_player ON aoe2_end.subscribe_id = aoe2_player.player_id AND group_id = %s
#             '''
#     subscribe_info = DB.execute_sqlP(sql,(group_id))
#     msg = '你的狙击名单如下:'
#     for sub in subscribe_info:
#         follower_id_list = json.loads(sub['follower_id_list'])
#         if user_id in follower_id_list['id_list']:
#             msg += '\n' + str(sub['subscribe_id']) + '·' + sub['player_name']
#     await matcher.finish(msg)


# @query.handle()
# async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
#     name = str(args).strip().lower()
#     DB = nonebot.get_driver().config.DB
#     sql = '''   SELECT *
#                 FROM aoe2_player
#                 WHERE player_name LIKE %s
#                 ORDER BY LENGTH(LOWER(player_name)) ASC, rating_tg DESC
#                 LIMIT 15'''
#     if len(name) <= 3:
#         player_tuples = DB.execute_sqlP(sql,(f'{name}'))
#     else :
#         player_tuples = DB.execute_sqlP(sql,(f'%{name}%'))
#     count = len(player_tuples)
#     if count == 0:
#         await matcher.finish('没有此玩家或者尚未录入该玩家')
#     else:
#         message = '玩家列表如下:'
#         for index,p in enumerate(player_tuples):
#             rating_1v1 = p['rating_1v1'] if p['rating_1v1'] else '---'
#             rating_tg = p['rating_tg'] if p['rating_tg'] else '---'
#             country = p['country'] if p['country'] else 'unknow'
#             message += f"\n{p['player_id']}·{p['player_name']}·({rating_1v1}/{rating_tg})·{country}"
#         await matcher.finish(message)
