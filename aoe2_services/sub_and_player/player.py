from nonebot import on_command

from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg

from ...AsyncDB import DatabaseConnectionPool



player_info = on_command("查询",priority=1)
sub_player = on_command("订阅")
cancle_sub = on_command("取消订阅")
sub_list = on_command("订阅列表")
turn_sub = on_command("调整订阅")
turn_end = on_command("调整狙击")

@player_info.handle()
async def _(event: MessageEvent, arg = CommandArg()):
    arg = str(arg)
    db = DatabaseConnectionPool()
    player_list = []
    name = arg.strip()
    complete_match_sql = "select player_id from aoe2_player where player_name = %s"
    aka_sql = "select id from aoe2_aka where name = %s"
    fuzzy_match_sql = "select player_id from aoe2_player where player_name like %s"
    results = await db.execute_query(complete_match_sql, (name,))
    if len(results) > 0:
        player_list = [r for r in results]
        await player_info.finish(str(player_list))
    # 别名匹配查询
    results = await db.execute_query(aka_sql, (name,))
    if len(results) > 0:
        player_list = [r for r in results]
        await player_info.finish(str(player_list))

    results = await db.execute_query(fuzzy_match_sql, (f"%{name}%",))
    if len(results) > 0:
        player_list = [r for r in results]
        await player_info.finish(str(player_list))
    await player_info.finish("没有找到该玩家")