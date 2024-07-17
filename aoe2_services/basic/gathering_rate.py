from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.params import CommandArg, ArgPlainText
from ..utils.common_utils import load_json_file
from .process import get_gathering_rate_base64_image

resource = on_command(".资源", priority=5)

@resource.handle()
async def _(bot: Matcher, event: MessageEvent, args: Message = CommandArg()):
    arg = str(args)
    civName = arg.split(" ")[0]
    age = int(arg.split(" ")[1])
    civNameDict = await load_json_file(r"./data/AOE/civName.json")
    if civName not in civNameDict:
        await bot.finish("未找到该文明")
        
    ageName = ["黑暗", "封建", "城堡", "帝王"]
    msg = f"正在查询{civName}{ageName[age-1]}时代资源采集速率"
    msg = msg.replace("中国", "联通")
    await bot.send(msg)
    civName = civNameDict[civName]
    # 将Base64字符串转换为图片消息
    image_msg = MessageSegment.image(await get_gathering_rate_base64_image(civName, age))

    # 发送图片消息给用户
    await bot.send(image_msg)

