from nonebot.log import logger

from ..utils.align_str import align_strings
from ...AsyncDB import DatabaseConnectionPool
from ..common.process import draw_msg


class Player:
    def __init__(self, player_id, player_name, rating_1v1, rating_tg, country):
        self.id = int(player_id)
        self.name = player_name
        self.rating_1v1 = int(rating_1v1)
        self.rating_tg = int(rating_tg)
        self.country = country


async def get_player_by_id(player_id: int) -> Player:
    db = DatabaseConnectionPool()
    sql = "SELECT player_name, rating_1v1, rating_tg, country FROM aoe2_player WHERE player_id = %s"
    try:
        player = await db.execute_query(sql, player_id)
    except Exception as e:
        logger.error(f"Error fetching player info: {e}")
        raise Exception('未找到对应玩家')
    else:
        if not player:
            raise Exception('未找到对应玩家')
        return Player(player_id, player[0], player[1], player[2], player[3])


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


async def get_sub_player_msg(qq_id: int, group_id: int):
    sub_player_list = await get_sub_player_list(qq_id, group_id)
    if not sub_player_list:
        return None
    msg = '\n'.join(align_strings(sub_player_list))
    return draw_msg(msg)


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
