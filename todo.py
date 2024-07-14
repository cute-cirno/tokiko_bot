from nonebot.matcher import Matcher
from nonebot import on_command
from typing import Tuple
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.permission import SUPERUSER
import nonebot
from nonebot.adapters import Message
from nonebot.params import CommandArg, RawCommand
from nonebot.exception import FinishedException

todo = on_command("todo", aliases={"挖坑", "填坑", "还有多少坑要填", "看看坑"})


@todo.handle()
async def _(
    matcher: Matcher,
    event: MessageEvent,
    args: Message = CommandArg(),
    rawCommand: str = RawCommand(),
):
    user_id = event.get_user_id()
    DB = nonebot.get_driver().config.DB
    # message = f"user:{user_id},type:{type(user_id)}\nthing:{thing}\ncommand:{command}\nrawCommand:{rawCommand}"
    # await matcher.send(message)n
    if rawCommand in ["挖坑"]:
        try:
            sql = "insert into todo_list (user_id,thing) values (%s,%s)"
            DB.startTransaction()
            DB.ExecuteNonQueryP(sql, (user_id, args))
            DB.commit()
            await matcher.finish("OK")
        except FinishedException:
            pass
        except Exception as e:
            DB.rollback()
            await matcher.finish(f"{e}")
    elif rawCommand in ["还有多少坑要填", "看看坑"]:
        try:
            sql = "select * from todo_list where user_id = %s and completed = 0"
            record_table = DB.execute_sqlP(sql, (user_id))
            if len(record_table) == 0:
                message = "很棒，一个坑都没有呢！"
                await matcher.finish(message)
            else:
                message = "你有这么多坑要填哦\n"
                id_list = []
                for index, record in enumerate(record_table):
                    message += f"{index+1}·{record['thing']}\n"
                    id_list.append(record["id"])
                message += "填坑直接填上序号即可"
                await matcher.finish(message)
        except FinishedException:
            pass
        except Exception as e:
            await matcher.finish(f"{e}")
    elif rawCommand in ["填坑"]:
        temp_id = int(str(args))
        message = "没问题，帮你划掉了这项"
        try:
            sql = "select * from todo_list where user_id = %s and completed = 0"
            record_table = DB.execute_sqlP(sql, (user_id))
            if (
                len(record_table) == 0
                or temp_id - 1 > len(record_table)
                or temp_id <= 0
            ):
                message = "没有坑或者序号大小不对呢"
                await matcher.finish(message)
            else:
                id_list = []
                for index, record in enumerate(record_table):
                    id_list.append(record["id"])
                real_id = id_list[temp_id - 1]
                sql = "update todo_list set completed = 1 where id = %s"
                DB.startTransaction()
                DB.ExecuteNonQueryP(sql, (real_id))
                DB.commit()
                await matcher.finish(message)
        except FinishedException:
            pass
        except Exception as e:
            DB.rollback()
            await matcher.finish(f"{e}")
