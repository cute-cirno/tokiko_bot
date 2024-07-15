import asyncio

from nonebot import get_driver, on_command
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg

from .config import ConfigModel,config
from .database import DatabaseConnectionPool

from nonebot import require
scheduler = require("nonebot_plugin_apscheduler").scheduler

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="MySQL Plugin",
    description="A plugin for interacting with MySQL database using aiomysql",
    usage="/mysql_query",
)

# 获取 nonebot 驱动
driver = get_driver()

@driver.on_startup
async def init_mysql_pool():
    db = await DatabaseConnectionPool.create(
        host=config.database_host,
        port=config.database_port,
        user=config.database_user,
        password=config.database_pwd,
        db=config.database_db,
        minsize=config.db_connection_minsize,
        maxsize=config.db_connection_maxsize,
    )
    asyncio.create_task(db.heartbeat())


mysql_query = on_command("sql", permission=SUPERUSER)


@mysql_query.handle()
async def handle_first_receive(
    matcher: Matcher,
    event: MessageEvent,
    args: Message = CommandArg(),
):
    arg = str(args)
    db = await DatabaseConnectionPool.create()
    sql_type = arg.split()[0].lower()
    try:
        if sql_type == "select":
            result = await db.execute_query(arg)
        else:
            result = await db.execute_update(arg)
        max_count = 5
        for r in result:
            if max_count > 0:
                await matcher.send(' '.join(map(str,r)))
                max_count -= 1
    except FinishedException as fe:
        pass
    except Exception as e:
        await matcher.finish(f"Query failed: {e}\n{result}")
