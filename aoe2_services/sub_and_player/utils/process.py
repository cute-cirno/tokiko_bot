from .data_handler import DataHandler
from datetime import datetime
from typing import cast, Union, Tuple, List, Any, Dict, Optional
from nonebot_plugin_txt2img import Txt2Img
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger
from httpx import AsyncClient

from ..model import OngoingRoom, LobbyRoom
from ...utils.align_str import align_strings
from ....AsyncDB import DatabaseConnectionPool

color_list = [None, "蓝", "紫", "绿", "黄", "青", "紫", "灰", "橙"]
civ_dict = {
    "Armenians": "亚美尼亚",
    "Aztecs": "阿兹特克",
    "Bengalis": "孟加拉",
    "Berbers": "柏柏尔",
    "Britons": "不列颠",
    "Bohemians": "波西米亚",
    "Bulgarians": "保加利亚",
    "Burgundians": "勃艮第人",
    "Burmese": "缅甸",
    "Byzantines": "拜占庭",
    "Celts": "凯尔特",
    "Chinese": "中国",
    "Cumans": "库曼",
    "Dravidians": "达罗毗荼",
    "Ethiopians": "埃塞俄比亚",
    "Franks": "法兰克",
    "Georgians": "格鲁吉亚",
    "Goths": "哥特",
    "Gurjaras": "瞿折罗",
    "Hindustanis": "印度斯坦",
    "Huns": "匈奴",
    "Incas": "印加",
    "Italians": "意大利",
    "Japanese": "日本",
    "Khmer": "高棉",
    "Koreans": "高丽",
    "Lithuanians": "立陶宛",
    "Magyars": "马扎尔",
    "Malay": "马来",
    "Malians": "马里",
    "Mayans": "玛雅",
    "Mongols": "蒙古",
    "Persians": "波斯",
    "Poles": "波兰",
    "Portuguese": "葡萄牙",
    "Romans": "罗马",
    "Saracens": "萨拉森",
    "Sicilians": "西西里",
    "Slavs": "斯拉夫",
    "Spanish": "西班牙",
    "Tatars": "鞑靼",
    "Teutons": "条顿",
    "Turks": "土耳其",
    "Vietnamese": "越南",
    "Vikings": "维京",
}


def check_player_and_get_room(
    args: str,
) -> Tuple[bool, List[Union[LobbyRoom, OngoingRoom]]]:
    if args.isdigit():
        arg = int(args)
    else:
        arg = args
    data_handler = DataHandler()
    room = data_handler.get_room(arg)
    if len(room[0]) == 0 and len(room[1]) == 0:
        return False, []
    room_list = []
    for lobby in room[0]:
        room_list.append(lobby)
    for ongoing in room[1]:
        room_list.append(ongoing)
    return True, room_list


def room2msg(room: Union[LobbyRoom, OngoingRoom]):
    room_type = room.status
    if room_type == "ongoing":
        room = cast(OngoingRoom, room)
        msg = f"房间ID:{room.id}+\n"
        msg += f"地图:{room.rms}\n"
        msg += f"开始于:{time_ago(room.started)}\n"
        msg += f"团队类型:{room.diplomacy}\n"
        msg += f"平均分数:{room.average_rating}\n"
        msg += f"玩家列表:昵称/颜色/文明/分数(单挑/组排)\n"
        msg += f"观战延迟:{room.spectating_delay}秒\n"
        player_info_list = []
        for player in room.players:
            if player.id == 0:
                player_info_list.append(
                    [
                        "AI",
                        f"{color_list[player.color]}",
                        civ_dict[player.civilization],
                        "----",
                        "----",
                    ]
                )
                continue
            player_info_list.append(
                [
                    player.name,
                    f"{color_list[player.color]}",
                    civ_dict[player.civilization],
                    f"{player.rating_1v1 if not player.rating_1v1 == 0 else '----'}",
                    f"{player.rating_tg if not player.rating_tg == 0 else '----'}",
                ]
            )
        player_info_list = align_strings(player_info_list)
        msg += "\n".join(player_info_list)
        return draw_msg(msg)


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


def get_all_room_msg():
    data_handler = DataHandler()
    lobby_count, ongoing_count = data_handler.room_count
    msg = f"大厅:{lobby_count}\n比赛:{ongoing_count}"
    return msg


def candidate_msg(room_list: List[LobbyRoom | OngoingRoom]):
    msg = "以下是你查询的房间：\n"
    index = 1
    lobby_align_str_list = []
    ongoing_align_str_list = []
    for room in room_list:
        if room.status == "lobby":
            lobby_align_str_list.append(
                [
                    f"{index}",
                    "大厅",
                    room.lobby,
                    f"{room.occupied_slots}/{room.slots}",
                ]
            )
        else:
            ongoing_align_str_list.append(
                [
                    f"{index}",
                    "对局",
                    f"地图{room.rms}" f"均分{room.average_rating}",
                ]
            )
    msg += "\n".join(align_strings(lobby_align_str_list))
    msg += "\n"
    msg += "\n".join(align_strings(ongoing_align_str_list))
    return draw_msg(msg)


async def get_player_id_list(player_name: str):
    db = DatabaseConnectionPool()
    queries = []
    if player_name.isdigit():
        queries.append(("select player_id from aoe2_player where player_id = %s",(int(player_name),)))
    queries.extend([
        ("select player_id from aoe2_player where player_name = %s", (player_name,)),
        ("select id from aoe2_aka where name = %s", (player_name,)),
        (
            "select player_id from aoe2_player where lower(player_name) like %s",
            (f"%{player_name.lower()}%",),
        ),
    ])

    for sql, params in queries:
        try:
            results = await db.execute_query(sql, params)
            if results:
                return [r[0] for r in results]
        except Exception as e:
            print(f"Failed to execute query: {sql} with params: {params}. Error: {e}")
            continue  # Optionally continue to next query on error, or handle differently

    return []  # Return an empty list if no IDs were found


async def get_player_info(player_id: int) -> dict | None:
    async with AsyncClient() as client:
        url = f"https://data.aoe2companion.com/api/profiles/{player_id}"
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None


async def get_smurf_list(player_id: int) -> Optional[List[Dict[str, Any]]]:
    async with AsyncClient() as client:
        url = f"https://smurf.new-chapter.eu/api/check_player?player_id={player_id}"
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["smurfs"][0]


async def get_player_info_msg(player_id: int):
    player_info = await get_player_info(player_id)
    if not player_info:
        return None
    steam_id = player_info.get("steamId")
    name = player_info.get("name")
    country = player_info.get("country")
    games = player_info.get("games")
    clan = player_info.get("clan")
    smurfs = await get_smurf_list(player_id)
    rating_list = [["排名", "当前/最高分", "排名"]]
    for l in player_info.get("leaderboards", []):
        rating_list.append(
            [l["leaderboards"], f'{l["rating"]}/{l["maxRating"]}', l["rank"]]
        )
    msg = ""
    msg += f"Steam ID: {steam_id}\n"
    msg += f"昵称: {name}\n"
    msg += f"工会: {clan}\n"
    msg += f"游戏场数: {games}\n"
    msg += f"国籍: {country}\n"
    msg += "\n".join(align_strings(rating_list))
    if not smurfs:
        return draw_msg(msg)
    msg += f"\n共享号:\n"
    for smurf in smurfs:
        msg += f'\n{smurf["name"]}({smurf["profile_id"]})'
    return draw_msg(msg)


def draw_msg(msg: str, font_size: int = 18):
    Txt2Img().set_font_size(font_size)
    pic = Txt2Img().draw("", msg)
    image = MessageSegment.image(pic)
    return image


async def get_candidate_msg(player_id_list: List[int]):
    db = DatabaseConnectionPool()
    placeholders = ", ".join(["%s"] * len(player_id_list))
    sql = f"SELECT
                player_id, player_name, rating_1v1, rating_tg, country
            FROM
                aoe2_player
            WHERE
                player_id IN ({placeholders})
            ORDER BY
                LENGTH(LOWER(player_name)) ASC, rating_tg DESC
            LIMIT 15"

    player_info_list: List[List[str]] = []
    player_info_list.append(["No.", "id", "昵称", "单排分", "组排分", "地区"])

    try:
        results = await db.execute_query(sql, player_id_list)
        for idx, record in enumerate(results):
            player_info_list.append(
                [f"{idx+1}. "]+([str(r) for r in record])
            )
    except Exception as e:
        logger.error(f"Error fetching player info: {e}")
    msg = "以下是待查询的玩家信息：\n"
    msg += "\n".join(align_strings(player_info_list))
    return draw_msg(msg)

class Player:
        def __init__(self, player_id, player_name, rating_1v1, rating_tg, country):
            self.id = int(player_id)
            self.name = player_name
            self.rating_1v1 = int(rating_1v1)
            self.rating_tg = int(rating_tg)
            self.country = country

async def get_player_by_id(player_id: int)->Optional[Player]:
    db = DatabaseConnectionPool()
    sql = "SELECT player_name, rating_1v1, rating_tg, country FROM aoe2_player WHERE player_id = %s"
    try:
        player = await db.execute_query(sql, player_id)
        if not player:
            return None
        return Player(player_id, player[0], player[1], player[2],player[3])
    except Exception as e:
        logger.error(f"Error fetching player info: {e}")
        

async def submit_sub_player(player_id: int, qq_id: int, group_id: int, mark_name: str) -> bool:
    db = DatabaseConnectionPool()
    sql = """
    INSERT INTO aoe2_fan (player_id, qq_id, group_id, sub, end, mark, create_time)
    VALUES (%s, %s, %s, 0, 0, %s, NOW())
    ON DUPLICATE KEY UPDATE
    sub = sub,
    end = end,
    mark = VALUES(mark),
    create_time = NOW();
    """
    try:
        rows_affected = await db.execute_update(sql, (player_id, qq_id, group_id, mark_name))
        return rows_affected > 0
    except Exception as e:
        print(f"Failed to execute query: Error: {e}")
        return False


async def cancle_sub_player_list(player_id_list: list[int], qq_id: int, group_id: int) -> int:
    db = DatabaseConnectionPool()
    placeholders = ', '.join(['%s'] * len(player_id_list))
    sql = f"""
    DELETE FROM aoe2_fan
    WHERE player_id IN ({placeholders}) AND qq_id = %s AND group_id = %s
    """
    # 需要将 player_id 列表和其他参数结合成一个元组作为参数传递给 SQL 语句
    params = tuple(player_id_list) + (qq_id, group_id)
    try:
        rows_affected = await db.execute_update(sql, params)
        return rows_affected
    except Exception as e:
        print(f"Failed to execute delete: Error: {e}")
        return 0
    
async def get_sub_player_list(qq_id: int, group_id: int):
    db = DatabaseConnectionPool()
    sub_sql = """
    SELECT
        player_id, sub, end, mark
    FROM
        aoe2_fan
    WHERE
        qq_id = %s AND group_id = %s
    """
    player_name_sql = """
    SELECT
        player_name
    FROM
        aoe2_player
    WHERE
        player_id = %s
    """
    try:
        results = await db.execute_query(sub_sql, (qq_id, group_id))
        sub_info_list = []
        for r in results:
            player_name = await db.execute_query(player_name_sql, r[0])
            sub_info_list.append([
                r[0],
                f"{player_name[0][0]}[{r[3]}]",
                "开" if r[1] else "关",
                "开" if r[2] else "关"
                ])
        return sub_info_list
    except Exception as e:
        print(f"Failed to execute query: Error: {e}")
        
async def get_sub_player_msg(qq_id: int, group_id: int):
    sub_player_list = await get_sub_player_list(qq_id, group_id)
    if not sub_player_list:
        return None
    msg = '\n'.join(align_strings(sub_player_list))
    return draw_msg(msg)

async def submit_turn_sub(player_id: int, qq_id: int, group_id: int):
    db = DatabaseConnectionPool()
    sql = """
    UPDATE
    aoe2_fan 
    SET
    sub = NOT sub,
    WHERE player_id = %s AND qq_id = %s AND group_id = %s
    """
    return await db.execute_update(sql, (player_id, qq_id, group_id))
    

async def submit_turn_end(player_id: int, qq_id: int, group_id: int):
    db = DatabaseConnectionPool()
    sql = """
    UPDATE
    aoe2_fan 
    SET
    end = NOT sub,
    WHERE player_id = %s AND qq_id = %s AND group_id = %s
    """
    return await db.execute_update(sql, (player_id, qq_id, group_id))