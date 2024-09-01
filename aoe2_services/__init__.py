import nonebot
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger

from .basic import *
from .career import *
from .datacenter import DataHandler
from .utils import CachedFileReader, Aoe2Browser

driver = get_driver()


@driver.on_startup
async def init_services():
    await CachedFileReader.create()
    await Aoe2Browser.init()
    auto_handler = DataHandler()
    await auto_handler.async_create("wss://aoe2recs.com/dashboard/api/", logger)