from typing import Optional

from nonebot import get_plugin_config
from pydantic import BaseModel

BaseConfigModel = (
    BaseModel
)


class ConfigModel(BaseConfigModel):
    DB_URL: Optional[str] = 'mysql://root:password@127.0.0.1:3306/mydatabase'


config = get_plugin_config(ConfigModel)
