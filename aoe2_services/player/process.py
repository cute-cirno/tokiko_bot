from nonebot.log import logger



from ..common.process import *








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