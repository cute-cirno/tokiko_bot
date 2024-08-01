from .data_handler import DataHandler
from datetime import datetime
from typing import cast
from nonebot_plugin_txt2img import Txt2Img
from nonebot.adapters.onebot.v11 import MessageSegment

from ..model import OngoingModel
from ...utils.align_str import align_strings

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
    "Hindustanis":"印度斯坦",
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
    "Vikings": "维京"
}


async def name_or_id_to_room_msg(args: str):
    if args.isdigit():
        arg = int(args)
    else:
        arg = args
    data_handler = DataHandler()
    room = await data_handler.get_room(arg)
    if not room:
        return
    room_type = room.status
    if room_type == "ongoing":
        room = cast(OngoingModel, room)
        msg = f"房间ID:{room.id}+\n"
        msg += f"地图:{room.rms}\n"
        msg += f"开始于:{time_ago(room.start_time)}\n"
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
        msg += '\n'.join(player_info_list)
            
        font_size = 18
        text = msg
        Txt2Img().set_font_size(font_size)
        pic = Txt2Img().draw('', text)
        msg = MessageSegment.image(pic)
        return msg

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