from typing import Optional
from nonebot import get_plugin_config
from pydantic import BaseModel

BaseConfigModel = (
    BaseModel
)


class ConfigModel(BaseConfigModel):
    base_url: Optional[str] = None


config = get_plugin_config(ConfigModel)
