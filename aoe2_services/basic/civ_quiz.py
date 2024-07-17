from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters import Message
from nonebot.params import CommandArg
from typing import List, Tuple

from ..utils.common_utils import load_json_file

civquiz = on_command(
    "哪些文明", aliases={"哪个文明", "哪些民族", "哪个民族", "那些民族"}, priority=5
)

@civquiz.handle()
async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    text = str(args)
    haveList, notHaveList = quiz_handler(text)
    if len(haveList)==0 and len(notHaveList)==0:
        await matcher.finish("未输入查询单位")
    result = await choseCiv(haveList, notHaveList)
    civlist = result[0]
    invalidlist = result[1]
    if len(invalidlist) > 0:
        msg = "不匹配的项目:" + ''.join(invalidlist)
        await matcher.finish(msg)
    if len(civlist) > 0:
        msg = f"有{len(civlist)}个文明:\n"
        msg += ' '.join(civlist)
    else:
        msg = "没有这样的文明"
    await matcher.send(msg)

def quiz_handler(text: str) -> Tuple[List[str], List[str]]:
    text = text.replace(",", " ").replace("，", " ").replace("?", "").replace("？", "")
    haveList = []
    notHaveList = []

    if "没有" in text:
        parts = text.split("没有")
        front = parts[0].strip()
        tail = parts[1].strip()

        if len(front) != 0:
            front = front.replace("有", "")
            haveList = front.strip().split()
            notHaveList = tail.strip().split()
        else:
            notHaveList = tail.strip().split()

        if "有" in tail:
            parts = tail.split("有")
            notHaveList = parts[0].strip().split()
            haveList = parts[1].strip().split()
    else:
        text = text.replace("有", "")
        haveList = text.strip().split()
    return (haveList, notHaveList)


async def choseCiv(havelist: list, nothavelist: list) -> Tuple[List[str], List[str]]:
    infodict = await load_json_file(r"./data/AOE/IDInfoDict_checked.json")
    allCivlist = set(infodict["building_87"]["availCivsCnameList"])
    invalidlist = []
    cname_map = {v["Cname"]: v for v in infodict.values()}
    for itemname in havelist:
        if itemname in cname_map:
            civlist = set(cname_map[itemname]["availCivsCnameList"])
            allCivlist &= civlist
        else:
            invalidlist.append(itemname)

    # 处理没有列表
    for itemname in nothavelist:
        if itemname in cname_map:
            civlist = set(cname_map[itemname]["notAvailCivsCnameList"])
            allCivlist &= civlist
        else:
            invalidlist.append(itemname)
    allCivlist = list(allCivlist)
    return (allCivlist, invalidlist)