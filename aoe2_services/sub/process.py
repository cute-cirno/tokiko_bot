from tortoise.exceptions import IntegrityError
from nonebot.log import logger

from ..utils.align_str import align_strings
from ..common.process import draw_msg
from ..AsynOrm.models import Aoe2Fan, Aoe2Player
from tortoise.exceptions import DoesNotExist
from datetime import datetime


class Player:
    def __init__(self, player_id, player_name, rating_1v1, rating_tg, country):
        self.id = int(player_id)
        self.name = player_name
        self.rating_1v1 = int(rating_1v1)
        self.rating_tg = int(rating_tg)
        self.country = country


async def get_player_by_id(player_id: int) -> Player:
    try:
        player = await Aoe2Player.get(player_id=player_id)
        return Player(
            player_id=player.player_id,
            player_name=player.player_name,
            rating_1v1=player.rating_1v1,
            rating_tg=player.rating_tg,
            country=player.country
        )
    except DoesNotExist:
        logger.error(f"Player with ID {player_id} not found")
        raise Exception('未找到对应玩家')


async def submit_sub_player(player_id: int, qq_id: int, group_id: int, mark_name: str) -> bool:
    try:
        fan_record, created = await Aoe2Fan.update_or_create(
            player_id=player_id,
            qq_id=qq_id,
            group_id=group_id,
            defaults={
                'sub': 0,
                'end': 0,
                'mark': mark_name,
                'create_time': datetime.now()  # 需要导入 datetime
            }
        )
        return True
    except IntegrityError as e:
        logger.error(f"Error updating or creating fan record: {e}")
        return False


async def cancle_sub_player_list(player_id_list: list[int], qq_id: int, group_id: int) -> int:
    try:
        # 批量删除操作
        rows_affected = await Aoe2Fan.filter(
            player_id__in=player_id_list,
            qq_id=qq_id,
            group_id=group_id
        ).delete()
        return rows_affected
    except Exception as e:
        logger.error(f"Failed to execute delete: Error: {e}")
        return 0


async def get_sub_player_msg(qq_id: int, group_id: int):
    sub_player_list = await get_sub_player_list(qq_id, group_id)
    if not sub_player_list:
        return None

    msg = '\n'.join(align_strings(sub_player_list))
    return draw_msg(msg)


async def get_sub_player_list(qq_id: int, group_id: int) -> list[list[str]]:
    try:
        # 查询子玩家信息
        results_info_list = await Aoe2Fan.filter(qq_id=qq_id, group_id=group_id).all()

        sub_info_list = []

        # 遍历查询结果，获取玩家名称并格式化信息
        for info in results_info_list:
            try:
                player = await Aoe2Player.get(player_id=info.player_id)
                player_name = player.player_name
            except DoesNotExist:
                player_name = "Unknown Player"

            sub_info_list.append([
                str(info.player_id),
                f"{player_name[:15]} 『{info.mark}』" if info.mark else player_name,
                "开" if info.sub else "关",
                "开" if info.end else "关"
            ])
        return sub_info_list
    except Exception as e:
        print(f"Failed to execute query: Error: {e}")
        return []


async def submit_turn_sub(player_id: int, qq_id: int, group_id: int):
    try:
        # 获取指定记录
        fan_record = await Aoe2Fan.get(player_id=player_id, qq_id=qq_id, group_id=group_id)

        # 更新记录的 `sub` 字段
        fan_record.sub = not fan_record.sub
        await fan_record.save()  # 保存更改

        return True

    except DoesNotExist:
        return False  # 记录未找到


async def submit_turn_end(player_id: int, qq_id: int, group_id: int):
    try:
        # 获取指定记录
        fan_record = await Aoe2Fan.get(player_id=player_id, qq_id=qq_id, group_id=group_id)

        # 更新记录的 `end` 字段
        fan_record.end = not fan_record.end
        await fan_record.save()  # 保存更改

        return True

    except DoesNotExist:
        return False  # 记录未找到
