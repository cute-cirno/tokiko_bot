from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.params import CommandArg, ArgPlainText
from ..utils.common_utils import load_json_file, imagefile_to_base64
from process import getItembyList

item_query = on_command(
    "kj,",
    aliases={
        "kj，",
        "科技,",
        "科技，",
        "jz,",
        "jz，",
        "建筑,",
        "建筑，",
        "dw,",
        "dw，",
        "单位,",
        "单位，",
    },
    priority=5,
)


@item_query.handle()
async def _(
    matcher: Matcher, state: T_State, event: MessageEvent, args: Message = CommandArg()
):
    itemName = str(args)
    IDdict = await load_json_file(r"./data/AOE/allID.json")
    namedict = await load_json_file(r"./data/AOE/allName.json")
    
    if not await check_item_name(itemName):
        list_for_choose = await get_candidate_names(itemName)
        if len(list_for_choose)>0:
            message = "未查询到该项目,你也许想查询:"
            for index, i in enumerate(list_for_choose):
                message += f"\n{index + 1}·{i}"
                if index > 4:
                    break
            message += "\n请输入对应序号"
            state["list_for_choose"] = list_for_choose
            state["namedict"] = namedict
            state["IDdict"] = IDdict
        else:
            message = "没有这种东西"
        await matcher.send(message)
    else:
        imgCode = "base64://" + str(await getItembyList(IDdict[f"{itemName}"]))
        image_msg = MessageSegment.image(imgCode)
        await matcher.finish(image_msg)
        
async def check_item_name(name: str) -> bool:
    namedict = await load_json_file(r"./data/AOE/allName.json")
    return name in namedict["allName"]

async def get_candidate_names(itemName: str) -> list:
    namedict = await load_json_file(r"./data/AOE/allName.json")
    exclude_chars = {"兵", "舰", "骑", "象", "精", "锐"}

    filtered_item_name = ''.join([c for c in itemName if c not in exclude_chars])


    list_for_choose = list(set(
        name for name in namedict["allName"] if any(c in name for c in filtered_item_name)
    ))


    if list_for_choose:
        list_for_choose.sort(key=lambda x: sum(c in x for c in filtered_item_name), reverse=True)
        return list_for_choose
    else:
        raise ValueError("没有找到匹配的项目名称")
    
