import random
from API.general import getJSON_filter as getJSON
from API.general import getJSON_local as getJSON_local


def getLatestPatch():
    """ Gets latest league patch e.g. 13.16.1
    
    Parameters
    ----------
    n/a

    Returns
    -------
    ver : str
        Latest patch version

    """
    patchList = getJSON("https://ddragon.leagueoflegends.com/api/versions.json")
    ver = patchList[0]
    return ver

def checkRegion(region):
    if region.lower() == "kr" or region == "ru":
        region_f = region.lower()
    elif region.lower() == "oce":
        region_f = "oc1"
    else:
        region_f = region.lower() + str(1)

    return region_f

def getSummonerData(summoner_name, region, riot_token):
    """ Returns various summoner data

    Parameters
    ----------
    summoner_name : str
        User's name
    riot_token : str
    
    Returns
    -------


    """
    
    region_f = checkRegion(region)
    print("get summoner json")
    data = getJSON(f"https://{region_f}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={riot_token}")
    print("json success")
    summoner_puuid = data["puuid"]
    summoner_name_case = data["name"]
    name_url = summoner_name_case.replace(" ", "%20")
    summoner_icon = data["profileIconId"]
    summoner_level = data["summonerLevel"]
    account_id = data["id"]
    return summoner_name_case, summoner_puuid, summoner_puuid, summoner_icon, summoner_level, account_id, name_url

def getSummonerIcon(icon_id):
    """ Returns summoner icon from ddragon CDN

    Parameters
    ----------

    Returns
    -------
    src : str
        URL to raw image
    """
    src = f'https://ddragon.leagueoflegends.com/cdn/{getLatestPatch()}/img/profileicon/{icon_id}.png'
    return src
def nameFilter(champName):
    exempt = ["LeeSin","KogMaw","MasterYi","MissFortune","MonkeyKing","RekSai","TahmKench"]
    exempt_lower = ["leesin","kogmaw","masteryi","missfortune","monkeyking","reksai","tahmkench"]

    if champName.lower() not in exempt_lower:
        champName_out = champName.capitalize()
    elif champName.lower() in exempt_lower:
        for x in range(len(exempt_lower)):
            if champName.lower() == exempt_lower[x]:
                champName_out = exempt[x]
    return champName_out

def getChampionName(championId):
    """
    
    Parameters
    ----------
    championId : int
        Unique champion id (can be found on ddragon)

    Returns
    -------
    championName : str
        Desired champions display name
    """

    champList = getJSON(f"http://ddragon.leagueoflegends.com/cdn/{getLatestPatch()}/data/en_US/championFull.json")["keys"]
    champName = "Couldn't retrieve champion name"    
    try:
        champName = champList[f'{championId}']
        return champName
    except:
        pass

def getChampionName_weekly(championId, champList):
    """
    
    Parameters
    ----------
    championId : int
        Specific champion ID (can be found in ddragon)
    
    champList : Dict
        Dictionary of desired champions in form id:name

    Returns
    -------
    championName : str
        Desired champions display name
    """

    #champList = getJSON(f"http://ddragon.leagueoflegends.com/cdn/{getLatestPatch()}/data/en_US/championFull.json")["keys"]
    champName = "Couldn't retrieve champion name"    
    try:
        champName = champList[f'{championId}']
        return champName
    except:
        pass



def getChampionID(championName):
    champName = nameFilter(championName)
    champList = getJSON(f"http://ddragon.leagueoflegends.com/cdn/{getLatestPatch()}/data/en_US/champion.json")["data"]

    champId = champList[champName]["key"]
    return champId

def getChampionData(championName):
    """
     
    Parameters
    ----------

    Returns
    -------
    """
    champName_f = nameFilter(championName)
    champList = getJSON(f"http://ddragon.leagueoflegends.com/cdn/{getLatestPatch()}/data/en_US/championFull.json")["data"]
    try:
        champData = champList[str(champName_f)]
        #print(champData)
        champion_name = champData["name"]
        #print(champion_name)
        champion_title = champData["title"]
        #print(champion_title)
        champion_lore = champData["lore"]
        #print(champion_lore)
        champion_icon = f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{champData["key"]}.png'
        ""
        #print(champion_icon)
        champion_splash = f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/{champData["key"]}/{champData["key"]}000.jpg'
        #print(champion_splash)
        champion_tags = ""
        for tag in champData["tags"]:
            champion_tags += tag + ", "
        champion_stats = champData["stats"]
        champion_resource = champData["partype"]
        try:
            champ_tips = champData["allytips"] + champData["enemytips"]
            tip = champ_tips[random.randint(0, (len(champ_tips)-1))]
        except:
            tip = "None given"
        return champion_name, champion_title, champion_lore, champion_icon, champion_splash, champion_tags, champion_stats, champion_resource, tip
    except:
        return "Invalid Champion Name", "", None, None, None, None, None, None, None

def masteryData(account_id, riot_token):
    
    mastery = getJSON(f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{account_id}?api_key={riot_token}")
    highestMastery = mastery[0]
    return mastery, highestMastery

def highestMasteryData(account_id, riot_token, region):


    region_f = checkRegion(region)
    data = getJSON(f"https://{region_f}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{account_id}?api_key={riot_token}")[0]
    masteryPoints = data["championPoints"]
    if data["chestGranted"] == True:
        chestGranted = "Yes"
    else:
        chestGranted = "No"
    
    if data["championLevel"] == 7:
        tokenStatus = "Complete"
    else:
        tokenStatus = f'{data["tokensEarned"]} tokens'
    
    championId = data["championId"]
    championLevel = data["championLevel"]
    
    return masteryPoints, chestGranted, tokenStatus, championId, championLevel

def masterySearch(account_id, champion_name, riot_token, region):


    region_f = checkRegion(region)
    champId = getChampionID(champion_name)
    mastery_data = getJSON(f"https://{region_f}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{account_id}/by-champion/{champId}?api_key={riot_token}")

    
    masteryPoints = mastery_data["championPoints"]
    if mastery_data["chestGranted"] == True:
        chestGranted = "Yes"
    else:
        chestGranted = "No"
    
    if mastery_data["championLevel"] == 7:
        tokenStatus = "Complete"
    elif mastery_data["championLevel"] <= 4:
        tokenStatus = f'{mastery_data["championPoints"]:,}/{(mastery_data["championPoints"]+mastery_data["championPointsUntilNextLevel"]):,}'
    else:
        tokenStatus = f'{mastery_data["tokensEarned"]} tokens'
    
    championId = mastery_data["championId"]
    championLevel = mastery_data["championLevel"]

    return masteryPoints, chestGranted, tokenStatus, championId, championLevel

def getWeeklyRotation(riot_token):
    champions = getJSON(f"https://euw1.api.riotgames.com/lol/platform/v3/champion-rotations?api_key={riot_token}")["freeChampionIds"]
    champList = getJSON(f"http://ddragon.leagueoflegends.com/cdn/{getLatestPatch()}/data/en_US/championFull.json")["keys"]

    names = []
    for x in champions:
        
        names.append(getChampionName_weekly(x, champList))

    names.sort()

    return names

def getLiveGame(riot_token, account_id, region, summonerEmojiList):

    region_f = checkRegion(region)
    try:
        isInGame = True
        
        liveData = getJSON(f'https://{region_f}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{account_id}?api_key={riot_token}')
        print("json loaded")
        gameQueueId = liveData["gameQueueConfigId"]
        print("gametype identified")


        mapInfo = queueData(gameQueueId)
        playerList = []
        print("doing recursion")
        for i in range(10):
            playerList.append(liveData["participants"][i]["summonerName"])
            if liveData["participants"][i]["summonerId"] == account_id:
                champion = liveData["participants"][i]["championId"]
                summoners = (liveData["participants"][i]["spell1Id"]),(liveData["participants"][i]["spell2Id"])
                champion_icon = f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{champion}.png'
                champion = getChampionName(champion)
        print("recursion done")
        summonerEmoji = summonerEmojiList[str(summoners[0])] , summonerEmojiList[str(summoners[1])]

        bansBlue = []
        bansRed = []
        #banTeamB = []
        try:
            for i in range(5):
                bansBlue.append(getChampionName(liveData["bannedChampions"][i]["championId"]))
                #banTeamB.append(liveData["bannedChampions"][i]["teamId"])
            
            
            #banTeamR = []
            for i in range(5, 10):
                bansRed.append(getChampionName(liveData["bannedChampions"][i]["championId"]))
                #banTeamR.append(liveData["bannedChampions"][i]["teamId"])
        except:
            print("skipped recursion")
            bansBlue = ["None"]
        bans = [bansBlue, bansRed]
    except:
        isInGame = False
        playerList = None
        mapInfo = None
        champion = None
        champion_icon = None
        bans = None
        summonerEmoji = None

    

    return isInGame, playerList, mapInfo, champion, bans, champion_icon, summonerEmoji

def queueData(id):

    queues = getJSON("https://static.developer.riotgames.com/docs/lol/queues.json")
    for i in range(len(queues)):
        if queues[i]["queueId"] == id:
            mapName = queues[i]["map"]
            desc = queues[i]["description"]
            if desc == "Arena":
                pass
            else:
                desc = desc[:-6]
            notes = queues[i]["notes"]
            break
        
    return mapName, desc, notes




def getRankedData(riot_token, account_id, region):

    return ""