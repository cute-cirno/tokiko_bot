
from datetime import datetime
from httpx import AsyncClient

from nonebot.log import logger
from nonebot_plugin_txt2img import Txt2Img
from nonebot.adapters.onebot.v11 import MessageSegment
from ...AsyncDB import DatabaseConnectionPool
from ..utils.align_str import align_strings


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

async def get_player_id_list(player_name: str):
    db = DatabaseConnectionPool()
    queries = []
    if player_name.isdigit():
        queries.append(
            ("select player_id from aoe2_player where player_id = %s", (int(player_name),)))
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
            print(
                f"Failed to execute query: {sql} with params: {params}. Error: {e}")
            continue  # Optionally continue to next query on error, or handle differently

    return []  # Return an empty list if no IDs were found



async def get_candidate_msg(player_id_list: list[int]):
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

    player_info_list: list[list[str]] = []
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
