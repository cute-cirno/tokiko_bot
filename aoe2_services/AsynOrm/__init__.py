from nonebot import get_driver

from tortoise import Tortoise
from .config import config

driver = get_driver()


@driver.on_startup
async def init():
    await Tortoise.init(
        db_url= config.DB_URL,
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()