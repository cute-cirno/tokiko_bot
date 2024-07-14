import asyncio

from nonebot import get_driver, on_command
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg
from .config import config

from database import MySQLPool

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
    await MySQLPool.create_instance(
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
    state: dict,
    args: Message = CommandArg(),
):
    args = str(event.get_message()).strip()
    if args:
        state["query"] = args


@mysql_query.got("query", prompt="Please input your MySQL query:")
async def handle_query(matcher: Matcher, event: MessageEvent, state: dict):
    query = state["query"]
    db = await MySQLPool.create_instance()
    try:
        result = await db.execute_query(query)
        await matcher.finish(f"Query Result: {result}")
    except Exception as e:
        await matcher.finish(f"Query failed: {e}")
