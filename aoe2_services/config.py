from typing import Optional

from cookit.pyd import get_model_with_config
from nonebot import get_plugin_config
from nonebot.compat import PYDANTIC_V2
from pydantic import BaseModel

BaseConfigModel = (
    BaseModel
)


class ConfigModel(BaseConfigModel):
    base_url: Optional[str] = None


config = get_plugin_config(ConfigModel)
