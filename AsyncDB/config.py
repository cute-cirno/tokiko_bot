from typing import Optional

from cookit.pyd import get_model_with_config
from nonebot import get_plugin_config
from nonebot.compat import PYDANTIC_V2
from pydantic import BaseModel

BaseConfigModel = (
    get_model_with_config({"coerce_numbers_to_str": True}) if PYDANTIC_V2 else BaseModel
)


class ConfigModel(BaseConfigModel):
    database_host: Optional[str] = "127.0.0.1"
    database_port: int = None
    database_user: Optional[str] = "root"
    database_pwd: Optional[str] = None
    database_db: Optional[str] = None
    db_connection_minsize: int = 2
    db_connection_maxsize: int = 10


config = get_plugin_config(ConfigModel)
