from typing import Optional

from nonebot import get_plugin_config
from pydantic import BaseModel

BaseConfigModel = BaseModel


class ConfigModel(BaseConfigModel):
    database_host: Optional[str] = "127.0.0.1"
    database_port: int = 3306
    database_user: Optional[str] = "root"
    database_pwd: Optional[str] = None
    database_db: Optional[str] = None
    db_connection_minsize: int = 2
    db_connection_maxsize: int = 10


config = get_plugin_config(ConfigModel)
