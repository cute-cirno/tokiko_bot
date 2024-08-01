# import nonebot
# import asyncio
# import json
# from nonebot.adapters.onebot.v11 import MessageEvent,MessageSegment,Message
# from nonebot import require
# from nonebot.adapters import Bot
# scheduler = require("nonebot_plugin_apscheduler").scheduler

# @scheduler.scheduled_job('interval', seconds=10)
# async def check_sub():
#     try:
#         bot = nonebot.get_bots()['3546848002']
#     except Exception as e:
#         print('error:',e)
#         return
#     DB = nonebot.get_driver().config.DB
    
#     sql = 'select * from aoe2_sub'
#     subscribe_info = DB.execute_sql(sql)

    
#     sub_dict = {} # 订阅信息字典{group_id:{sub_id:[followers]}}
#     sub_id_list = set() 
#     for record in subscribe_info:
#         qq_list = json.loads(record['follower_id_list'])['id_list']
#         sub_id = record['subscribe_id']
#         group_id = record['group_id']
#         if group_id not in sub_dict:
#             sub_dict[group_id] = {}
#         if sub_id not in sub_dict[group_id]:
#             sub_dict[group_id][sub_id] = qq_list
#         else:
#             sub_dict[group_id][sub_id].extend(qq_list)
#         sub_id_list.add(sub_id)
    
#     await push_lobby_sub(bot,sub_dict,sub_id_list)
#     await push_ongoing_sub(bot,sub_dict,sub_id_list)
    
        
# @scheduler.scheduled_job('interval', seconds=9)
# async def check_end():
#     try:
#         bot = nonebot.get_bots()['3546848002']
#     except Exception as e:
#         print('error:',e)
#         return
#     DB = nonebot.get_driver().config.DB
    
#     sql = 'select * from aoe2_end'
#     subscribe_info = DB.execute_sql(sql)

    
#     sub_dict = {} # 订阅信息字典{group_id:{sub_id:[followers]}}
#     sub_id_list = set() 
#     for record in subscribe_info:
#         qq_list = json.loads(record['follower_id_list'])['id_list']
#         sub_id = record['subscribe_id']
#         group_id = record['group_id']
#         if group_id not in sub_dict:
#             sub_dict[group_id] = {}
#         if sub_id not in sub_dict[group_id]:
#             sub_dict[group_id][sub_id] = qq_list
#         else:
#             sub_dict[group_id][sub_id].extend(qq_list)
#         sub_id_list.add(sub_id)
#     ongoing = nonebot.get_driver().config.ongoing
#     end_checked = nonebot.get_driver().config.end_checked
#     end_game = nonebot.get_driver().config.end_game
#     id_room_dict = nonebot.get_driver().config.id_room_dict
#     marked_room = nonebot.get_driver().config.marked_room
    
#     for k,o in ongoing.items():
#         if k in end_checked:
#             continue
#         for p in o['players']:
#             id = p['id'] if 'id' in p else 0
#             if id in sub_id_list:
#                 id_room_dict[id] = k
#                 marked_room.add(k)
#         end_checked.add(k)
#     need_push_sub_id = set()
#     for room in end_game:
#         if room in marked_room:
#             for sub_id,room_id in id_room_dict.items():
#                 if room == room_id:
#                     need_push_sub_id.add(sub_id)
#                     try:
#                         marked_room.remove(room)
#                     except KeyError as e:
#                         pass
#     end_game = set()
#     for group_id,info in sub_dict.items():
#         name_list = set()
#         at_list = []
#         for sub_id,qq_list in info.items():
#             if sub_id not in need_push_sub_id:
#                 continue
#             sql = 'select * from aoe2_player where player_id = %s'
#             player_info = DB.execute_sqlP(sql,(sub_id))
#             name_list.add(player_info[0]['player_name'])
#             at_list.extend(qq_list)
#         name_list = list(name_list)
#         at_list = list(set(at_list))
#         if len(name_list) == 0 or len(at_list) == 0:
#             continue
#         tip = ''
#         for name in name_list:
#             tip += f"{name}\n"
#         tip += f"以上玩家游戏结束，请速速准备狙击"
#         message_list = [tip]
#         [message_list.append(MessageSegment.at(int(_))) for _ in at_list]
#         await bot.call_api('send_group_msg', **{'group_id': int(group_id), 'message': Message(message_list)})
        
        
# async def push_lobby_sub(bot:Bot,sub_dict:dict,sub_id_list:list):
#     DB = nonebot.get_driver().config.DB
#     lobby = nonebot.get_driver().config.lobby
#     lobby_checked = nonebot.get_driver().config.lobby_checked
    
#     need_push_sub_id = set()
#     need_push_link = {}
#     for k,l in lobby.items():
#         if k in lobby_checked:
#             continue
#         for p in l['players']:
#             id = p['id'] if 'id' in p else 0
#             if id in sub_id_list:
#                 need_push_sub_id.add(id)
#                 need_push_link[id] = l['link']
#         lobby_checked.add(k)
                
#     for group_id,info in sub_dict.items():
#         name_list = set()
#         at_list = []
#         link_msg = ''
#         for sub_id,qq_list in info.items():
#             if sub_id not in need_push_sub_id:
#                 continue
#             sql = 'select * from aoe2_player where player_id = %s'
#             player_info = DB.execute_sqlP(sql,(sub_id))
#             name_list.add(player_info[0]['player_name'])
#             at_list.extend(qq_list)
#             link_msg += need_push_link[sub_id]+'\n'
#         name_list = list(name_list)
#         at_list = list(set(at_list))
#         if len(name_list) == 0 or len(at_list) == 0:
#             continue
#         tip = ''
#         for name in name_list:
#             tip += f"{name}\n"
#         tip += f"以上被订阅的玩家进入了大厅,房间为\n{link_msg}"
#         message_list = [tip]
#         [message_list.append(MessageSegment.at(int(_))) for _ in at_list]
#         await bot.call_api('send_group_msg', **{'group_id': int(group_id), 'message': Message(message_list)})
        
        
# async def push_ongoing_sub(bot:Bot,sub_dict:dict,sub_id_list:list):
#     DB = nonebot.get_driver().config.DB
#     ongoing = nonebot.get_driver().config.ongoing
#     sub_ckecked = nonebot.get_driver().config.sub_checked
    
#     need_push_sub_id = set()
#     need_push_link = {}
    
#     for k,o in ongoing.items():
#         if k in sub_ckecked:
#                 continue
#         for p in o['players']:
#             id = p['id'] if 'id' in p else 0
#             if id in sub_id_list:
#                 need_push_sub_id.add(id)
#                 need_push_link[id] = o['link']
#         sub_ckecked.add(k)
#     for group_id,info in sub_dict.items():
#         name_list = set()
#         at_list = []
#         link_msg = ''
#         for sub_id,qq_list in info.items():
#             if sub_id not in need_push_sub_id:
#                 continue
#             sql = 'select * from aoe2_player where player_id = %s'
#             player_info = DB.execute_sqlP(sql,(sub_id))
#             name_list.add(player_info[0]['player_name'])
#             at_list.extend(qq_list)
#             link_msg += need_push_link[sub_id]+'\n'
#         name_list = list(name_list)
#         at_list = list(set(at_list))
#         if len(name_list) == 0 or len(at_list) == 0:
#             continue
#         tip = ''
#         for name in name_list:
#             tip += f"{name}\n"
#         tip += f"以上被订阅的玩家开始了游戏,链接为\n{link_msg}"
#         message_list = [tip]
#         [message_list.append(MessageSegment.at(int(_))) for _ in at_list]
#         await bot.call_api('send_group_msg', **{'group_id': int(group_id), 'message': Message(message_list)})
        
        
# @scheduler.scheduled_job('interval', hours=12)
# async def delete_empty_sub():
#     DB = nonebot.get_driver().config.DB
#     sql = '''delete from aoe2_sub where follower_id_list like '{"id_list": []}';'''
#     DB.ExecuteNonQuery(sql)