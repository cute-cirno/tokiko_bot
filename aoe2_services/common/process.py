
from datetime import datetime
from httpx import AsyncClient

from nonebot.log import logger
from nonebot_plugin_txt2img import Txt2Img
from nonebot.adapters.onebot.v11 import MessageSegment
from ..utils.align_str import align_strings
from ..AsynOrm.models import Aoe2Player, Aoe2Aka
from tortoise.exceptions import  OperationalError


def time_ago(timestamp):
    current_time = datetime.now()
    past_time = datetime.fromtimestamp(timestamp)

    time_difference = current_time - past_time

    if time_difference.days > 365:
        return f"{time_difference.days // 365}年前"
    elif time_difference.days > 30:
        return f"{time_difference.days // 30}月前"
    elif time_difference.days > 0:
        return f"{time_difference.days}天前"
    elif time_difference.seconds // 3600 > 0:
        return f"{time_difference.seconds // 3600}小时前"
    elif time_difference.seconds // 60 > 0:
        return f"{time_difference.seconds // 60}分钟前"
    else:
        return "刚才"


async def get_player_info(player_id: int) -> dict | None:
    async with AsyncClient() as client:
        url = f"https://data.aoe2companion.com/api/profiles/{player_id}"
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None


async def get_smurf_list(player_id: int) -> list[dict[str, object]]:
    async with AsyncClient() as client:
        url = f"https://smurf.new-chapter.eu/api/check_player?player_id={player_id}"
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["smurfs"][0]
        raise Exception('该玩家无小号')


def draw_msg(msg: str, font_size: int = 18):
    Txt2Img().set_font_size(font_size)
    pic = Txt2Img().draw("", msg)
    image = MessageSegment.image(pic)
    return image


# async def get_player_id_list(player_name: str):
#     db = DatabaseConnectionPool()
#     queries = []

#     if player_name.isdigit():
#         queries.append(
#             ("select player_id from aoe2_player where player_id = %s", (int(player_name),)))
#     queries.extend([
#         ("select player_id from aoe2_player where player_name = %s", (player_name,)),
#         ("select player_id from aoe2_aka where name = %s", (player_name,)),
#         (
#             "select player_id from aoe2_player where lower(player_name) like %s",
#             (f"%{player_name.lower()}%",),
#         ),
#     ])

#     for sql, params in queries:
#         try:
#             results = await db.execute_query(sql, params)
#             if results:
#                 return [r["player_id"] for r in results]
#         except Exception as e:
#             print(
#                 f"Failed to execute query: {sql} with params: {params}. Error: {e}")
#             continue  # Optionally continue to next query on error, or handle differently

#     return []  # Return an empty list if no IDs were found

async def get_player_id_list(player_name: str):
    queries = []

    if player_name.isdigit():
        queries.append(Aoe2Player.filter(player_id=int(
            player_name)).values_list('player_id', flat=True))

    queries.extend([
        Aoe2Player.filter(player_name=player_name).values_list(
            'player_id', flat=True),
        Aoe2Aka.filter(name=player_name).values_list('player_id', flat=True),
        Aoe2Player.filter(player_name__icontains=player_name.lower()).values_list(
            'player_id', flat=True),
    ])

    for query in queries:
        try:
            results = await query
            if results:
                return list(results)
        except OperationalError as e:
            print(f"查询执行失败: {e}")
            continue  # 可选择继续下一个查询或以其他方式处理
    raise


# async def get_candidate_msg(player_id_list: list[int]):
#     db = DatabaseConnectionPool()
#     placeholders = ", ".join(["%s"] * len(player_id_list))
#     sql = f"SELECT
#                 player_id, player_name, rating_1v1, rating_tg, country
#             FROM
#                 aoe2_player
#             WHERE
#                 player_id IN ({placeholders})
#             ORDER BY
#                 LENGTH(LOWER(player_name)) ASC, rating_tg DESC
#             LIMIT 15"

#     player_info_list: list[list[str]] = []
#     player_info_list.append(["No.", "id", "昵称", "单排分", "组排分", "地区"])

#     try:
#         results = await db.execute_query(sql, player_id_list)
#         for idx, record in enumerate(results):
#             player_info_list.append(
#                 [f"{idx+1}. "]+([str(r) for r in record.values()])
#             )
#     except Exception as e:
#         logger.error(f"Error fetching player info: {e}")
#     msg = "以下是待查询的玩家信息：\n"
#     msg += "\n".join(align_strings(player_info_list))
#     return draw_msg(msg)

# 异步函数获取候选信息
async def get_candidate_msg(player_id_list: list[int]):
    player_info_list: list[list[str]] = []
    player_info_list.append(["No.", "id", "昵称", "单排分", "组排分", "地区"])

    try:
        # 使用 ORM 查询
        results = await Aoe2Player.filter(player_id__in=player_id_list)\
            .order_by("player_name", "-rating_tg")\
            .limit(15)\
            .all()

        for idx, record in enumerate(results):
            player_info_list.append(
                [f"{idx+1}. ", str(record.player_id), record.player_name, str(record.rating_1v1), str(record.rating_tg), record.country]
            )
    except Exception as e:
        logger.error(f"Error fetching player info: {e}")
    
    # 格式化消息内容
    msg = "以下是待查询的玩家信息：\n"
    msg += "\n".join(align_strings(player_info_list))
    return draw_msg(msg)