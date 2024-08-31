import nonebot
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger

from .basic.civ_quiz import *
from .basic.civ_query import *
from .basic.gathering_rate import *
from .basic.item_query import *
from .career import *
from .datacenter.data_handler import *
from .sub_and_player import *
from .utils.cache_utils import CachedFileReader
from .utils.browser_utils import Aoe2Browser
from .datacenter.sub_pusher import SubPusher

driver = get_driver()


@driver.on_startup
async def init_services():
    await CachedFileReader.create()
    await Aoe2Browser.init()
    auto_handler = DataHandler()
    await auto_handler.async_create("wss://aoe2recs.com/dashboard/api/", logger)


class OnebotPusher(SubPusher):
    def __init__(self) -> None:
        super().__init__()

    async def _push(self, group_id: int, push_info: dict):
        at_msg_list = [MessageSegment.at(qq_id)
                       for qq_id in push_info.get("at_set", set())]
        bot = nonebot.get_bot()
        await bot.call_api('send_group_msg', **{'group_id': group_id, 'message': push_info})

    # async def get_name_nickname_info(self, player_info: dict[int, list[str]]) -> dict[str, list[str]]:
    #     pass
