import asyncio

from nonebot import get_driver, on_command
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.params import CommandArg
from nonebot_plugin_txt2img import Txt2Img
from nonebot.log import logger

from .config import config
from .database import DatabaseConnectionPool

from nonebot import require
scheduler = require("nonebot_plugin_apscheduler").scheduler

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="MySQL Plugin",
    description="A plugin for interacting with MySQL database using aiomysql",
    usage="sql sql_sentence",
)

# 获取 nonebot 驱动
driver = get_driver()


@driver.on_startup
async def init_mysql_pool():
    await DatabaseConnectionPool.async_create(
        host=config.database_host,
        port=config.database_port,
        user=config.database_user,
        password=config.database_pwd,
        db=config.database_db,
        minsize=config.db_connection_minsize,
        maxsize=config.db_connection_maxsize,
    )


mysql_query = on_command("sql", permission=SUPERUSER)


@mysql_query.handle()
async def handle_first_receive(
    matcher: Matcher,
    event: MessageEvent,
    args: Message = CommandArg(),
):
    arg = str(args)
    db = await DatabaseConnectionPool.async_create()
    sql_type = arg.split()[0].lower()
    try:
        msg = ''
        if sql_type in {'select', 'desc', 'show'}:
            result = await db.execute_query(arg)
            if result:
                # 获取表头
                headers = result[0].keys()
                msg += ' '.join(map(str, headers)) + '\n'
                max_count = 20
                for r in result:
                    if max_count > 0:
                        # 添加数据行
                        msg += ' '.join(map(str, r.values())) + '\n'
                        max_count -= 1
        else:
            result = await db.execute_update(arg)
            if result == 0:
                msg = "没有匹配的记录"
            else:
                msg = f"OK，{result}行已被更改"

        font_size = 18
        text = msg
        txt2img = Txt2Img()
        txt2img.set_font_size(font_size)
        pic = txt2img.draw('', text)
        msg = MessageSegment.image(pic)
        await matcher.finish(msg)
    except FinishedException:
        pass
    except Exception as e:
        logger.error(f"Query failed: {e}")
        await matcher.finish(f"Query failed: {e}")
