import random
from API.general import getJSON_filter as getJSON
from API.general import getJSON_local as getJSON_local
from API.general import timeElapsed
from API.general import unpackList
from re import sub
from matplotlib import pyplot as plt
from PIL import Image
import urllib.request as rq

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
    print(account_id)
    return summoner_name_case, summoner_puuid, summoner_puuid, summoner_icon, summoner_level, account_id, name_url

def getRankedData(riot_token, summoner_id, region):
    region_f = checkRegion(region)
    print("doing ranked json")
    rankedInfo = getJSON(f"https://{region_f}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={riot_token}")
    if rankedInfo != []:
        for i in range(len(rankedInfo)):
            if rankedInfo[i]["queueType"] == "RANKED_FLEX_SR" or rankedInfo[i]["queueType"] == "RANKED_SOLO_5x5":
        
                print("has ranked info")
                queueType = rankedInfo[0]["queueType"]
                tier = rankedInfo[0]["tier"]
                rank = rankedInfo[0]["rank"]
                rankIcon = f"https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/images/ranked-mini-crests/{tier.lower()}.png"
                wins = rankedInfo[0]["wins"]
                losses = rankedInfo[0]["losses"]
                leaguePoints = rankedInfo[0]["leaguePoints"]
                hasRank = True
                return hasRank, rankIcon, queueType, tier, rank,  wins, losses, leaguePoints
            else:
                print("no ranked info")
                hasRank = False
                rankIcon = "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/images/ranked_crest_placeholder_2.png"
                return hasRank, rankIcon
    else:
        print("no ranked info")
        hasRank = False
        rankIcon = "https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-static-assets/global/default/images/ranked_crest_placeholder_2.png"
        return hasRank, rankIcon

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
    champName = champName.replace(" ", "").replace("'", "")
    if champName.lower() == "wukong":
        champName = "monkeyking"
    exempt = ["LeeSin","KogMaw","MasterYi","MissFortune","MonkeyKing","RekSai","TahmKench","TwistedFate"]
    exempt_lower = ["leesin","kogmaw","masteryi","missfortune","monkeyking","reksai","tahmkench","twistedfate"]

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

def removeClientFormatting(text):

    return sub('<.*?>', '', text)

def getRuneInfo(runes, runeList):
    """
    """
    runesOut = []
    print("doing runes")
    try:
        for rune in runes:
            for i in range(len(runeList)):
                for x in range(len(runeList[i]["slots"])):
                    for n in range(len(runeList[i]["slots"][x]["runes"])):
                        if runeList[i]["slots"][x]["runes"][n]["id"] == rune:
                            print("rune found")
                            runeFound = True
                            runeName = runeList[i]["slots"][x]["runes"][n]["name"]
                            runeDesc = removeClientFormatting(runeList[i]["slots"][x]["runes"][n]["shortDesc"])
                            runesOut.append((runeName, runeDesc))
        return runeFound, runesOut
    except:

        return False

def getItemName(itemId, itemList):

    itemName = itemList[f"{itemId}"]["name"]
    print(itemName)
    return itemName

def getChampionID(championName):
    champName = nameFilter(championName)
    champList = getJSON(f"http://ddragon.leagueoflegends.com/cdn/{getLatestPatch()}/data/en_US/champion.json")["data"]
    try:
        champId = champList[champName]["key"]
        return champId
    except:
        return NameError



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
        champion_icon = f'http://ddragon.leagueoflegends.com/cdn/{getLatestPatch()}/img/champion/{champName_f}.png'
        ""
        #print(champion_icon)
        champion_splash = f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/{champData["key"]}/{champData["key"]}000.jpg'
        #print(champion_splash)
        champion_tags = ""
        """for tag in champData["tags"]:
            if tag != champData["tags"][len(champData["tags"])-1]:
                champion_tags += tag + ", "
            else:
                champion_tags += tag"""
        champion_tags = unpackList(champData["tags"], True)
        champion_stats = champData["stats"]
        champion_resource = champData["partype"]
        champion_skins = []
        for skin in champData["skins"]:
            champion_skins.append(skin["name"])
        print(champion_skins)

        try:
            champ_tips = champData["allytips"] + champData["enemytips"]
            tip = champ_tips[random.randint(0, (len(champ_tips)-1))]
        except:
            tip = None
        return champion_name, champion_title, champion_lore, champion_icon, champion_splash, champion_tags, champion_stats, champion_resource, tip, champion_skins, champName_f
    except:
        return "Invalid Champion Name", "", None, None, None, None, None, None, None, None, None

def getItemData(itemName):
    """
     
    Parameters
    ----------

    Returns
    -------
    """
    itemName = itemName.replace(" ", "")
    itemList = getJSON(f"http://ddragon.leagueoflegends.com/cdn/{getLatestPatch()}/data/en_US/item.json")["data"]
    # http://ddragon.leagueoflegends.com/cdn/13.16.1/img/item/1018.png
    itemId = ""
    build_path = []
    builds_into = []
    for item in itemList:
        if itemList[item]["name"].lower().replace(" ", "") == itemName.lower():
            print(itemList[item]["name"])
            itemId = itemList[item]["image"]["full"]
            print(itemId)
            itemCost = itemList[item]["gold"]["total"]
            itemCombine = itemList[item]["gold"]["base"]
            itemSell = itemList[item]["gold"]["sell"]
            itemDesc = itemList[item]["plaintext"]
            itemName_f = itemList[item]["name"]
            try:
                for component in itemList[item]["from"]:
                    print(component)
                    build_path.append(getItemName(component, itemList))
                
            except:
                pass
            try:
                for component in itemList[item]["into"]:
                    print(component)
                    builds_into.append(getItemName(component, itemList))
                
            except:
                pass

    itemIcon = f'http://ddragon.leagueoflegends.com/cdn/{getLatestPatch()}/img/item/{itemId}'
    print(itemIcon)
    
    return itemIcon, itemCost, itemDesc, itemName_f, build_path, builds_into, itemCombine, itemSell


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

def getSummonerEmotes(summonerEmojiList, summoners):
    return summonerEmojiList[str(summoners[0])] , summonerEmojiList[str(summoners[1])]

def getRuneEmotes(runeList, runes):
    runeEmoji = []
    for i in range(len(runes)):
            runeEmoji.append(runeList[str(runes[i])])
    return runeEmoji


def getLiveGame(riot_token, account_id, region, summonerEmojiList, runeList):

    region_f = checkRegion(region)
    try:
        isInGame = True
        
        liveData = getJSON(f'https://{region_f}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{account_id}?api_key={riot_token}')
        gameQueueId = liveData["gameQueueConfigId"]
        print("player is in game")


        mapInfo = queueData(gameQueueId)
        playerList = []
        for i in range(10):
            playerList.append(liveData["participants"][i]["summonerName"])
            if liveData["participants"][i]["summonerId"] == account_id:
                champion = liveData["participants"][i]["championId"]
                runes = liveData["participants"][i]["perks"]["perkIds"][:-3]
                summoners = (liveData["participants"][i]["spell1Id"]),(liveData["participants"][i]["spell2Id"])
                champion_icon = f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{champion}.png'
                champion = getChampionName(champion)

        summonerEmoji = getSummonerEmotes(summonerEmojiList, summoners)
        runeEmoji = getRuneEmotes(runeList, runes)
        runeInfo = getRuneInfo(runes, getJSON(f"http://ddragon.leagueoflegends.com/cdn/{getLatestPatch()}/data/en_US/runesReforged.json"))
        print(runeInfo)
        gameStartTime = int(str(liveData["gameStartTime"])[:-3])
        print(gameStartTime)
        gameDuration = timeElapsed(gameStartTime)


        bansBlue = []
        bansRed = []
        try:
            for i in range(5):
                bansBlue.append(getChampionName(liveData["bannedChampions"][i]["championId"]))
            
            
            #banTeamR = []
            for i in range(5, 10):
                bansRed.append(getChampionName(liveData["bannedChampions"][i]["championId"]))
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
        gameDuration = None
        runeInfo = None
        runeEmoji = None

    

    return isInGame, playerList, mapInfo, champion, bans, champion_icon, summonerEmoji, gameDuration, runeEmoji


def getMatchHistory(riot_token, puuid, region, count):
    region = checkRegion(region)
    print(region)
    print(puuid)
    if region == "euw1" or region == "eun1":
        region_f = "europe"
    elif region == "na1" or region == "la1" or region == "la2":
        region_f = "americas"
    elif region == "kr" or region == "jp1":
        region_f = "asia"
    else:
        region_f = "sea"

    #"AMERICAS, EUROPE, ASIA, SEA"
    try:
        matchHistorySuccess = True
        matchIds = getJSON(f"https://{region_f}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}&api_key={riot_token}")
        matches = []
        for i in range(len(matchIds)):
            matches.append(getJSON(f"https://{region_f}.api.riotgames.com/lol/match/v5/matches/{matchIds[i]}?api_key={riot_token}"))
        puuid = puuid
        champName = []
        win = []
        role = []
        gameType = []
        for match in matches:
            gameType.append(queueData(match["info"]["queueId"])[1])
            for i in range(len(match["info"]["participants"])):
                    if match["info"]["participants"][i]["puuid"] == puuid:
                        champName.append(match["info"]["participants"][i]["championName"])
                        if match["info"]["participants"][i]["win"] == True:
                            win.append(":white_check_mark: Win")
                        else:
                            win.append(":x: Loss")
                        role.append(match["info"]["participants"][i]["individualPosition"].capitalize())
        return matchHistorySuccess, [champName, win, role, gameType], [matchIds, region_f]

    except:
        matchHistorySuccess = False
        return matchHistorySuccess, ""


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

def drawMap(riot_token, gameId, region, mapType):
    gameLink = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{gameId}/timeline?api_key={riot_token}"

    

    print(gameLink)
    game = getJSON(gameLink)["info"]["frames"]
    blueId = [1, 2, 3, 4, 5]
    redId = [6, 7, 8, 9, 10]
    x_blue = []
    x_red = []
    y_blue = []
    y_red = []

    for frame in game:
        for event in frame["events"]:
            if event["type"] == "CHAMPION_KILL":
                if event["killerId"] in blueId:
                    x_blue.append(event["position"]["x"])
                    y_blue.append(event["position"]["y"])
                else:
                    x_red.append(event["position"]["x"])
                    y_red.append(event["position"]["y"])

    red_kills = len(x_red)
    blue_kills = len(x_blue)
    # bypass image restrictions
    opener=rq.build_opener()
    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    rq.install_opener(opener)

    if mapType == "5v5 ARAM":
        url='https://raw.communitydragon.org/latest/game/assets/maps/info/map12/2dlevelminimap.png'
        print(" is aram")
    else:
        url='https://raw.communitydragon.org/latest/game/assets/maps/info/map11/2dlevelminimap.png'
    local='map'
    rq.urlretrieve(url,local)


    img = Image.open("map")
    img.show()


    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    im = plt.imread("map")
    fig, ax = plt.subplots()
    if mapType == "5v5 ARAM":
        im = ax.imshow(im, extent=[0, 12300, 0, 12300])
    else:
        im = ax.imshow(im, extent=[0, 16000, 0, 16000])

    ax.plot(x_blue, y_blue,  marker=".", markersize=20, markeredgecolor="red", markerfacecolor="blue", linestyle="None")
    ax.plot(x_red, y_red,  marker=".", markersize=20, markeredgecolor="blue", markerfacecolor="red", linestyle="None")
    ax.set_axis_off()
    plt.plot()
    print("saving file")
    plt.savefig(f"src\\files\\LeagueMaps\{gameId[:2]}\{gameId}.png", bbox_inches='tight', pad_inches=0)
    #plt.show()

    return red_kills, blue_kills