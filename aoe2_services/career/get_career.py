import httpx

async def getCareerMsg(id:int):
    url = "https://api.ageofempires.com/api/v2/AgeII/GetMPFull"
    payload = {
        "profileId": f"{id}",
        "gamertag": None,
        "playerNumber": 0,
        "gameId": 0,
        "matchType": "3"
        }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if not response:
            return None
        data = response.json()
        career = data['careerStats']
        # print(f'Response JSON: {data}')  # 假设返回的是JSON格式
        
    msg = ""
    civList = career['civilizations']
    defeatCivList = sorted(civList,key=lambda x:x['defeatCount'])
    defeatCivList.reverse()
    winCivList = sorted(civList,key=lambda x:x['winCount'])
    winCivList.reverse()
    msg += f"\t{data['user']['userName']}陛下！在帝国生涯中，您指挥了大大小小{career['totalGames']}场战斗，其中{career['totalWins']}场战斗以您的胜利而告终。"
    msg += f"您最擅长带领{winCivList[0]['name']}、{winCivList[1]['name']}和{winCivList[2]['name']}的士兵，"
    msg += f"您指挥他们赢得了{sum([winCivList[0]['winCount'],winCivList[1]['winCount'],winCivList[2]['winCount']])}场战斗。"
    msg += f"在对抗外族的战斗中，您在面对{defeatCivList[0]['name']}、{defeatCivList[1]['name']}和{defeatCivList[2]['name']}时表现优异，"
    msg += f"总计击退他们{sum([defeatCivList[0]['defeatCount'],defeatCivList[1]['defeatCount'],defeatCivList[2]['defeatCount']])}次。\n"
    msg += f"\t你的战斗生涯中获得的单次最高总分是{career['highScoreTotal']}；另外，您的最高军事分为{career['highScoreMilitary']}，"
    msg += f"最高经济分为{career['highScoreEconomy']}，最高科技分为{career['highScoreTechnology']}。"
    msg += f"在您指挥的战斗中，您的部队击杀了{career['unitsKilled']}名敌人，但也付出了{career['unitsLost']}人的代价，一将功成万骨枯，莫过如此。\n"
    msg += f"\t您的部队在您的指挥下攻城拔寨，总计攻陷了{career['buildingsRaised']}座建筑，但是在战火中，您也有{career['buildingsLost']}座建筑被敌军烧毁。"
    msg += f"在社会建设方面，您的人民为帝国建立了{career['wondersBuilt']}座奇观以及{career['castlesBuilt']}座城堡，帝国的城堡为你生产了{career['trebsBuilt']}架巨型投石机供您攻城拔寨。"
    msg += f"在您的领导下，帝国的人口蒸蒸日上，快活的农民们已经播种良田{career['farmsBuilt']}轮次，在战火中还请您多关照他们。"
    return msg

