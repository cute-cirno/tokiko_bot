
from datetime import datetime
from httpx import AsyncClient

from nonebot_plugin_txt2img import Txt2Img
from nonebot.adapters.onebot.v11 import MessageSegment

from ..utils.align_str import align_strings
from ..datacenter.dashboard import Room
from ..datacenter.data_handler import DataHandler
from ..common import Const


color_list = Const.color_list
civ_dict = Const.civ_dict


def check_player_and_get_room(args: str,) -> list[Room]:
    data_handler = DataHandler()
    return data_handler.dashboard.get_room(args)


def room2msg(room: Room):
    room_type = room.status
    if room_type == "ongoing":
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
    lobby_count = data_handler.dashboard.lobby_count
    ongoing_count = data_handler.dashboard.ongoing_count
    msg = f"大厅:{lobby_count}\n比赛:{ongoing_count}"
    return msg


def candidate_msg(room_list: list[Room]):
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
