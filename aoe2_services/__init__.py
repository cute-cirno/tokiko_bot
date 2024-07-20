from nonebot import get_driver
from .utils.cache_utils import CachedFileReader
from .utils.browser_utils import Aoe2Browser

from .basic.civ_quiz import *
from .basic.civ_query import *
from .basic.gathering_rate import *
from .basic.item_query import *
from career import *

driver = get_driver()

@driver.on_startup
async def init_services():
    await CachedFileReader.create()
    await Aoe2Browser.init()