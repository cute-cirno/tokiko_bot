import asyncio

from ..utils.browser_utils import Aoe2Browser
from ..utils.common_utils import image_to_base64
from ..config import config


async def getItembyList(iteminfo: list) -> str:
    if not config.base_url:
        raise ValueError("base_url is not set in config")
    else:
        base_url = config.base_url
    
    browser_instance = Aoe2Browser()
    browser = await browser_instance.get_browser()
    if iteminfo[0] == "Normal":
        url = base_url + "/?lng=zh#Spanish"
    else:
        url = base_url + f"/?lng=zh#{iteminfo[3]}"
    try:
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1200, "height": 2000})
        await page.goto(url)
        element1 = await page.wait_for_selector(f"#{iteminfo[2]}")
        if element1 is None:
            raise ValueError("Element not found")
        await element1.click()
        element2 = await page.query_selector("#advanced-stats")
        await asyncio.sleep(0.1)
        if element2 is None:
            raise ValueError("Element not found")
        await element2.click()
        await asyncio.sleep(0.1)

        element_handle = await page.query_selector("#helptext__content")
        if not element_handle:
            raise ValueError("Element not found")
        needChangeList = []
        [needChangeList.append(_) for _ in await element_handle.query_selector_all("p")]
        [
            needChangeList.append(_)
            for _ in await element_handle.query_selector_all("h3")
        ]

        extra_element = await page.query_selector("#helptext__advanced_stats")
        if not extra_element:
            raise ValueError("Element not found")
        [needChangeList.append(_) for _ in await extra_element.query_selector_all("p")]
        [needChangeList.append(_) for _ in await extra_element.query_selector_all("h3")]

        avaiCiv_handle = await page.query_selector("#helptext__x_ref")
        if not avaiCiv_handle:
            raise ValueError("Element not found")
        needChangeList.append(await avaiCiv_handle.query_selector("h3"))

        # uselessTag = ['#helptext__content > p.helptext__desc','#helptext__content > p.helptext__upgrade_info']
        # uselessText = [await page.query_selector(_) for _ in uselessTag]
        # uselessText.append(await element2.query_selector('summary'))
        # for i in uselessText:
        #     await i.evaluate('(e) => e.remove()')

        for i in needChangeList:
            classname = await i.get_attribute("class")
            if classname and (
                classname in ("helptext__upgrade_cost", "helptext__heading")
            ):
                continue
            text = replaceWord(await i.inner_text())
            await i.evaluate(f'(e) => e.textContent = "{text}"')
        infobox = await page.query_selector("#helptext")
        if not infobox:
            raise ValueError("Element not found")
        await asyncio.sleep(0.1)
        image = await infobox.screenshot()
        await page.close()
        return image_to_base64(image)
    except Exception:
        if page:
            await page.close()
        raise
    
def replaceWord(text: str) -> str:
    replaceWords = [
        ("HP", "生命"),
        ("Upgrade", "升级"),
        ("Stats", "属性"),
        ("Attack:", "攻击力:"),
        ("Armor:", "甲:"),
        ("Pierce armor", "盾"),
        ("Min Range", "最小射程"),
        ("Range", "射程"),
        ("Line of Sight", "LOS"),
        ("Speed", "速度"),
        ("Build Time", "建造时间"),
        ("Frame Delay", "帧延迟"),
        ("Attack Delay", "攻击延迟"),
        ("Reload Time", "攻击间隔"),
        ("Accuracy", "精确度"),
        ("Spearmen", "枪兵"),
        ("Standard Buildings", "标准建筑"),
        ("Base Pierce", "远程伤害"),
        ("High Pierce Armor Siege Units", "高防器械"),
        ("Stone Defense & Harbors", "石质防事 & 海港"),
        ("Base Melee", "近战伤害"),
        ("All Archers", "射手"),
        ("Obsolete", "废弃建筑"),
        ("UPGRADE", "升级费用"),
        ("STATS", "属性"),
        ("ATTACKS", "攻击标签"),
        ("ARMOURS", "护甲标签"),
        ("CIVILIZATIONS", "可用文明"),
        ("Research Time", "研究时间"),
        ("Repeatable", " "),
        ("Siege Units", "攻城武器"),
        ("Cavalry Resistance", "骑兵抗性"),
        ("Mounted Archers", "骑射手"),
        ("Mounted Units", "马上单位"),
        ("Unique Units", "特殊单位"),
        ("Walls & Gates", "墙 & 门"),
        ("All Buildings", "所有建筑"),
        ("Castles & Kreposts", "城堡 & 营垒"),
        ("Garrison", "驻扎数"),
        ("Camels", "骆驼"),
        ("Fishing Ships", "渔船"),
        ("Infantry", "步兵"),
        ("Monks", "僧侣"),
        ("Wonders", "奇观"),
        ("Gunpowder Units", "火药单位"),
        ("Mamelukes", "马穆鲁克"),
        ("Ships", "舰船"),
        ("Skirmishers", "掷矛手"),
        ("Eagle Warriors", "鹰勇士"),
        ("Condottieri", "佣兵"),
    ]
    for i in replaceWords:
        text = text.replace(i[0], i[1])
    return text