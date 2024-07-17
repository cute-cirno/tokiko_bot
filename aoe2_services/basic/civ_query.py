from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent
from nonebot.adapters import Message
from nonebot.params import CommandArg

from .process import get_civ_base64_image
from ..utils.common_utils import load_json_file,imagefile_to_base64


civ = on_command(
    "mz,",
    aliases={"mz，", "文明，", "文明,", "民族，", "民族,", "wm,", "wm，"},
    priority=5,
)

@civ.handle()
async def _(marcher: Matcher, event: MessageEvent, arg: Message = CommandArg()):
    civname = str(arg)
    if not await check_civ_name(civname):
        await marcher.finish("错误文明名称，请重试！")
    civName = await get_engname_by_civname(civname)
    image_msg = MessageSegment.image(await get_civ_base64_image(civname))
    # 发送图片消息给用户
    await marcher.send(image_msg)
    techtreeimg = MessageSegment.image(await imagefile_to_base64(f"./data/AOE/image/{civName}.png"))
    await marcher.finish(techtreeimg)
    

async def check_civ_name(civname: str) -> bool:
    civ_name_dict = await load_json_file(r"./data/AOE/civName.json")
    if civname in civ_name_dict:
        return True
    else:
        return False

async def get_engname_by_civname(civname: str) -> str:
    civ_name_dict = await load_json_file(r"./data/AOE/civName.json")
    return civ_name_dict[civname]
