import random
import numpy as np
from API.general import *
from re import sub
from matplotlib import pyplot as plt
from PIL import Image
import urllib.request as rq
from os import path, makedirs


async def cacheLatestPatch(filepath: str="src\\files\\lolLatestPatch.json"):
    """ Caches all League patch versions sorted by latest first
    
    Parameters
    ----------
    filepath : str
        Path to `.json` file to write to e.g. files\\lolLatestPatch.json
    """
    url = "https://ddragon.leagueoflegends.com/api/versions.json" # http://api.steampowered.com/ISteamApps/GetAppList/v0002
    await saveJSON(url=url, filepath=filepath)



async def getLatestPatch():
    """ Gets latest league patch e.g. 13.16.1
    
    Parameters
    ----------
    n/a

    Returns
    -------
    ver : str
        Latest patch version

    """
    patchList = await getJSON_local("src\\files\\lolLatestPatch.json")
    
    ver = patchList[0]
    return ver

async def checkRegion(region: str):
    """ Returns the correctly formatted region for Riot's web API

    Parameters
    ----------
    region : str
        Region to use in API e.g. euw, na, oce (not case sensitive)
    
    Returns
    -------
        region_f : str
            Region formatted correctly
    """
    if region.lower() == "kr" or region == "ru":
        region_f = region.lower()
    elif region.lower() == "oce":
        region_f = "oc1"
    else:
        region_f = region.lower() + str(1)

    return region_f

async def getSummonerData_old(summoner_name: str, region: str, riot_token: str):
    """ Returns various summoner data

    Parameters
    ----------
    summoner_name : str
        User's name
    region : str
        User's region e.g. euw, na (not case sensitive)
    riot_token : str
        Riot API token    

    Returns
    -------
    summoner_name_case : str
        Case correct version of summoner's name
    summoner_puuid : str
        Unique Riot PUUID for summoner
    summoner_puuid : str
        Duplicate (needs fixing)
    summoner_icon : str
        URL to icon (PNG)
    summoner_level : int
        Account level of summoner
    account_id : str
        Unique Riot ID for summoner
    name_url : str
        Formatted version of summoner name for use in URLs
    """

    #riot_id = await getJSON(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/jeet/roma?api_key={riot_token}")


    region_f = await checkRegion(region)
    data = await getJSON(f"https://{region_f}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={riot_token}")
    #print(f"https://{region_f}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={riot_token}")
    #data = f"https://{region_f}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{riot_id}?api_key={riot_token}"
    summoner_puuid = data["puuid"]
    summoner_name_case = data["name"]
    name_url = summoner_name_case.replace(" ", "%20")
    summoner_icon = data["profileIconId"]
    summoner_level = data["summonerLevel"]
    account_id = data["id"]
    return summoner_name_case, summoner_puuid, summoner_puuid, summoner_icon, summoner_level, account_id, name_url


async def getSummonerData(game_name: str, tagline: str, region: str, riot_token: str):
    """ Returns various summoner data
    """

    if not tagline:
        tagline = region

    #print(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tagline[1:] if tagline[0] == '#' else tagline}?api_key={riot_token}")
    riot_data = (await getJSON(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name.replace(' ', '%20')}/{tagline[1:] if tagline[0] == '#' else tagline}?api_key={riot_token}"))
    puuid, gameName, tagLine = riot_data["puuid"], riot_data["gameName"], riot_data["tagLine"]

    region_f = await checkRegion(region)
    
    #data = await getJSON(f"https://{region_f}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={riot_token}")
    print(f"https://{region_f}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={riot_token}")

    data = await getJSON(f"https://{region_f}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={riot_token}")


    summoner_puuid = data["puuid"]
    summoner_name_case = riot_data["gameName"]
    name_url = summoner_name_case.replace(" ", "%20")
    summoner_icon = data["profileIconId"]
    summoner_level = data["summonerLevel"]
    account_id = data["id"]
    
    return summoner_name_case, summoner_puuid, summoner_puuid, summoner_icon, summoner_level, account_id, name_url, gameName, tagLine

async def getRankedData(riot_token: str, summoner_id: str, region: str):
    """ Gets most ranked data for summoner. Attempts to find solo/duo -> flex if no solo/duo data

    Parameters
    ----------
    riot_token : str
        Riot API token  
    summoner_name : str
        User's name
    region : str
        User's region e.g. euw, na (not case sensitive)

    Returns
    -------
    hasRank : bool
        Whether player has rank or not
    rankIcon : str
        URL to icon corresponding to summoner rank
    queueType : int
        Only if hasRank is True. Type of queue (see Riot docs)
    tier : str
        Only if hasRank is True. Tier of rank e.g. gold, diamond
    rank : str
        Only if hasRank is True. Rank level - I,II,III or IV
    wins : int
        Only if hasRank is True. Number of ranked wins
    losses : int
        Only if hasRank is True. Number of ranked losses
    leaguePoints : int
        Only if hasRank is True. Amount of LP
    """
    region_f = await checkRegion(region)
    print("doing ranked json")
    rankedInfo = await getJSON(f"https://{region_f}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={riot_token}")
    print(f"https://{region_f}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={riot_token}")
    if rankedInfo != []:
        for info in rankedInfo:
            if info["queueType"] == "RANKED_FLEX_SR" or info["queueType"] == "RANKED_SOLO_5x5":
        
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

async def getSummonerIcon(icon_id: int):
    """ Returns summoner icon from ddragon CDN

    Parameters
    ----------
    icon_id : int
        Specific ID corresponding to icon (see Riot docs)

    Returns
    -------
    src : str
        URL to raw image
    """
    src = f'https://ddragon.leagueoflegends.com/cdn/{await getLatestPatch()}/img/profileicon/{icon_id}.png'
    return src

async def nameFilter(champName):
    champName = champName.replace(" ", "").replace("'", "")
    if champName.lower() == "wukong":
        champName = "monkeyking"
    exempt = ["LeeSin","KogMaw","MasterYi","MissFortune","MonkeyKing","RekSai","TahmKench","TwistedFate", "KSante", "XinZhao", "JarvanIV"]
    exempt_lower = ["leesin","kogmaw","masteryi","missfortune","monkeyking","reksai","tahmkench","twistedfate", "ksante", "xinzhao", "jarvaniv"]

    if champName.lower() not in exempt_lower:
        champName_out = champName.capitalize()
    elif champName.lower() in exempt_lower:
        for x in range(len(exempt_lower)):
            if champName.lower() == exempt_lower[x]:
                champName_out = exempt[x]
    return champName_out

async def getChampionName(championId: int):
    """ Returns name of champion given it's ID
    
    Parameters
    ----------
    championId : int
        Unique champion id (can be found on ddragon)

    Returns
    -------
    championName : str
        Desired champions display name
    """

    champList = await getJSON(f"http://ddragon.leagueoflegends.com/cdn/{await getLatestPatch()}/data/en_US/championFull.json")
    champName = "Couldn't retrieve champion name"
    try:
        champName_internal = champList["keys"][f'{championId}']
        champName = champList["data"][champName_internal]["name"]
        return champName
    except:
        return None

async def getChampionName_weekly(championId, champList):
    """ Duplicate of getChampionName without making multiple calls for multiple entries
    
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
        champName_internal = champList["keys"][f'{championId}']
        champName = champList["data"][champName_internal]["name"]
        return champName
    except:
        pass

async def removeClientFormatting(text: str):
    """ Removes the wacky formatting done to format text for the League Client

    Parameters
    ----------
    text : str
        Any text entry
    
    Returns
    -------
    out : str
        Input text with unnecessary formatting removed
    """
    return sub('<.*?>', '', text)

async def getRuneInfo(runes: list, runeList: list):
    """ Gets rune data from name search

    Parameters
    ----------
    runes : list
        List of runes to search for
    runeList : list
        Rune database list
    
    Returns
    -------
    runeFound : bool
        True if rune is found, False if couldn't find
    runesOut : list
        List containing tuples of (rune name, rune description)
    """
    runesOut = []
    print("doing runes")
    try:
        for rune in runes:
            for runes in runeList:
                for slot in rune["slots"]:
                    for rune_r in slot["runes"]:
                        if rune_r["id"] == rune:
                            print("rune found")
                            runeFound = True
                            runeName = rune_r["name"]
                            runeDesc = removeClientFormatting(rune_r["shortDesc"])
                            runesOut.append((runeName, runeDesc))
        return runeFound, runesOut
    except:

        return False

async def getItemName(itemId, itemList):

    itemName = itemList[f"{itemId}"]["name"]
    if itemList[f"{itemId}"].get("requiredAlly", False) == "Ornn":
        itemName = f"{itemName} <:ornn_circle:1207422369325514833>"
    
    return itemName

async def getChampionID(championName):
    champName = await nameFilter(championName)
    champList = (await getJSON(f"http://ddragon.leagueoflegends.com/cdn/{await getLatestPatch()}/data/en_US/champion.json"))["data"]
    try:
        champId = champList[champName]["key"]
        return champId
    except:
        return NameError

async def getChampionData(championName: str, nameOnly: bool=False):
    """
     
    Parameters
    ----------

    Returns
    -------
    """
    champName_f = await nameFilter(championName)
    latest_patch = await getLatestPatch()
    champList = (await getJSON(f"http://ddragon.leagueoflegends.com/cdn/{latest_patch}/data/en_US/championFull.json"))["data"]
    try:
        champData = champList[str(champName_f)]
        champion_name = champData["name"]
        if nameOnly:
            return champion_name
        champion_title = champData["title"]
        champion_lore = champData["lore"]
        champion_icon = f'http://ddragon.leagueoflegends.com/cdn/{latest_patch}/img/champion/{champName_f}.png'
        ""
        
        champion_splash = f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/{champData["key"]}/{champData["key"]}000.jpg'
        champion_tags = ""

        champion_tags = unpackList(champData["tags"], True)
        champion_stats = champData["stats"]
        champion_resource = champData["partype"]
        champion_skins = []
        for skin in champData["skins"]:
            champion_skins.append(skin["name"])
        #print(champion_skins)

        try:
            champ_tips = champData["allytips"] + champData["enemytips"]
            tip = champ_tips[random.randint(0, (len(champ_tips)-1))]
        except:
            tip = None
        return champion_name, champion_title, champion_lore, champion_icon, champion_splash, champion_tags, champion_stats, champion_resource, tip, champion_skins, champName_f
    except:
        if nameOnly:
            return "Invalid Champion Name"
        return "Invalid Champion Name", "", None, None, None, None, None, None, None, None, None

async def getItemData(itemName: str):
    """
     
    Parameters
    ----------

    Returns
    -------
    """
    itemName = itemName.replace(" ", "")
    latest_patch = await getLatestPatch()
    print(f"http://ddragon.leagueoflegends.com/cdn/{latest_patch}/data/en_US/item.json")
    itemList = (await getJSON(f"http://ddragon.leagueoflegends.com/cdn/{latest_patch}/data/en_US/item.json"))["data"]
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
            itemDetail = itemList[item]["description"]
            itemName_f = itemList[item]["name"]
            ornn = False

            if itemList[item].get("requiredAlly", False) == "Ornn":
                ornn = True

                


            
            try:
                for component in itemList[item]["from"]:
                    print(component)
                    build_path.append(await getItemName(component, itemList))

            except:
                pass
            try:
                for component in itemList[item]["into"]:
                    print(component)
                    builds_into.append(await getItemName(component, itemList))
                
            except:
                pass

    itemIcon = f'http://ddragon.leagueoflegends.com/cdn/{latest_patch}/img/item/{itemId}'
    print(itemIcon)
    
    return itemIcon, itemCost, itemDesc, itemName_f, build_path, builds_into, itemCombine, itemSell, ornn, itemDetail


async def highestMasteryData(account_id, riot_token, region):

    #
    # OUTDATED
    #

    region_f = await checkRegion(region)
    data = (await getJSON(f"https://{region_f}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{account_id}?api_key={riot_token}"))[0]
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

async def masterySearch(puuid, champion_name, riot_token, region):


    region_f = await checkRegion(region)
    champId = await getChampionID(champion_name)
    mastery_data = await getJSON(f"https://{region_f}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champId}?api_key={riot_token}")

    print(f"https://{region_f}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champId}?api_key={riot_token}")

    masteryPoints = mastery_data["championPoints"]
    tenPlus = 0

    # REMOVED FEATURE :(
    #if mastery_data["chestGranted"] == True:
    #    chestGranted = "Yes"
    #else:
    #    chestGranted = "No"
    
    
    championId = mastery_data["championId"]
    championLevel = mastery_data["championLevel"]
    last_played = mastery_data.get("lastPlayTime", None)
    last_level = mastery_data["championPointsUntilNextLevel"]

    return masteryPoints, championId, championLevel, last_played, last_level

def masteryFull(account_id, champion_name, riot_token, region):
    """empty function returns None"""
    #mastery_data = getJSON(f"https://{region_f}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{account_id}/by-champion/{champId}?api_key={riot_token}")
    return

async def getWeeklyRotation(riot_token: str):
    champions = (await getJSON(f"https://euw1.api.riotgames.com/lol/platform/v3/champion-rotations?api_key={riot_token}"))["freeChampionIds"]
    champList = await getJSON(f"http://ddragon.leagueoflegends.com/cdn/{await getLatestPatch()}/data/en_US/championFull.json")

    names = []
    for x in champions:
        
        names.append(await getChampionName_weekly(x, champList))

    names.sort()

    return names

async def getSummonerEmotes(summonerEmojiList, summoners):
    return summonerEmojiList[str(summoners[0])] , summonerEmojiList[str(summoners[1])]

async def getRuneEmotes(runeList, runes):
    runeEmoji = []
    for rune in runes:
            runeEmoji.append(runeList[str(rune)])
    return runeEmoji


async def getLiveGame(riot_token, account_id, region, summonerEmojiList, runeList):

    region_f = await checkRegion(region)
    try:
        isInGame = True
        
        liveData = await getJSON(f'https://{region_f}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{account_id}?api_key={riot_token}')
        gameQueueId = liveData["gameQueueConfigId"]
        print("player is in game")


        mapInfo = await queueData(gameQueueId)
        playerList = []
        for i in range(10):
            playerList.append(liveData["participants"][i]["summonerName"])
            if liveData["participants"][i]["summonerId"] == account_id:
                champion = liveData["participants"][i]["championId"]
                runes = liveData["participants"][i]["perks"]["perkIds"][:-3]
                summoners = (liveData["participants"][i]["spell1Id"]),(liveData["participants"][i]["spell2Id"])
                champion_icon = f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{champion}.png'
                champion = await getChampionName(champion)

        summonerEmoji = await getSummonerEmotes(summonerEmojiList, summoners)
        runeEmoji = await getRuneEmotes(runeList, runes)
        runeInfo = await getRuneInfo(runes, await getJSON(f"http://ddragon.leagueoflegends.com/cdn/{await getLatestPatch()}/data/en_US/runesReforged.json"))
        print(runeInfo)
        gameStartTime = int(str(liveData["gameStartTime"])[:-3])
        print(gameStartTime)
        gameDuration = gameStartTime#timeElapsed(gameStartTime)


        bansBlue = []
        bansRed = []
        try:
            for i in range(5):
                bansBlue.append(await getChampionName(liveData["bannedChampions"][i]["championId"]))
            
            
            #banTeamR = []
            for i in range(5, 10):
                bansRed.append(await getChampionName(liveData["bannedChampions"][i]["championId"]))
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


async def getMatchHistory(riot_token, puuid, region, count):
    region = await checkRegion(region)
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
        matchIds = await getJSON(f"https://{region_f}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}&api_key={riot_token}")
        matches = []
        for match in matchIds:
            matches.append(await getJSON(f"https://{region_f}.api.riotgames.com/lol/match/v5/matches/{match}?api_key={riot_token}"))
        puuid = puuid
        champName = []
        win = []
        role = []
        gameType = []
        for match in matches:
            gameType.append((await queueData(match["info"]["queueId"]))[1])
            for participants in match["info"]["participants"]:
                    if participants["puuid"] == puuid:
                        champName.append(await getChampionData(participants["championName"], nameOnly=True))
                        if participants["win"] == True:
                            win.append(":white_check_mark: Win")
                        else:
                            win.append(":x: Loss")
                        role.append(participants["individualPosition"].capitalize())
        
        return matchHistorySuccess, [champName, win, role, gameType], [matchIds, region_f]

    except:
        matchHistorySuccess = False
        return matchHistorySuccess, ""


async def queueData(id):

    queues = await getJSON("https://static.developer.riotgames.com/docs/lol/queues.json")
    for queue in queues:
        if queue["queueId"] == id:
            mapName = queue["map"]
            desc = queue["description"]
            if desc == "Arena":
                pass
            else:
                desc = desc[:-6]
            notes = queue["notes"]
            break
        
    return mapName, desc, notes

async def drawMap(riot_token, gameId, region, mapType, summoner_puuid):
    gameLink = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{gameId}/timeline?api_key={riot_token}"
    print(gameLink)

    #participants = gameLink["metadata"]["participants"]
    #print(participants)
    folder=f"src\\files\\LeagueMaps\{gameId[:2]}"
    game = (await getJSON(gameLink))["info"]["frames"]

    
    

    blueId = [1, 2, 3, 4, 5]
    redId = [6, 7, 8, 9, 10]
    x_blue = []
    x_red = []
    y_blue = []
    y_red = []
    kills = []

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



    # check if file exists and if not create
    if not path.isfile(f"{folder}\{gameId}.png"):
        if not path.isdir(folder):
            makedirs(folder, exist_ok=True)
        # bypass image restrictions
        opener=rq.build_opener()
        opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        rq.install_opener(opener)

        if mapType == "5v5 ARAM":
            url='https://raw.communitydragon.org/latest/game/assets/maps/info/map12/2dlevelminimap.png'
            print(" is aram")
        else:
            url='https://raw.communitydragon.org/latest/game/assets/maps/info/map11/2dlevelminimap.png'
        
        local='src/files/LeagueMaps/map.png'
        rq.urlretrieve(url,local)



        plt.rcParams["figure.figsize"] = [7.00, 3.50]
        plt.rcParams["figure.autolayout"] = True
        im = plt.imread(local)
        fig, ax = plt.subplots()
        if mapType == "5v5 ARAM":
            im = ax.imshow(im, extent=[0, 12300, 0, 12300])
        else:
            im = ax.imshow(im, extent=[0, 16000, 0, 16000])

        ax.plot(x_blue, y_blue,  marker=".", markersize=20, markeredgecolor="red", markerfacecolor="blue", linestyle="None", alpha=0.5)
        ax.plot(x_red, y_red,  marker=".", markersize=20, markeredgecolor="blue", markerfacecolor="red", linestyle="None", alpha=0.5)
        ax.set_axis_off()
        plt.plot()



        

        plt.savefig(f"{folder}\{gameId}.png", bbox_inches='tight', pad_inches=0)
        #plt.show()

    return red_kills, blue_kills

async def masteryGraph(riot_token, puuid, region):
    region_f = await checkRegion(region)

    mastery_data = await getJSON(f"https://{region_f}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}?api_key={riot_token}")
    print(f"https://{region_f}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}?api_key={riot_token}")
    champList = (await getJSON(f"http://ddragon.leagueoflegends.com/cdn/{await getLatestPatch()}/data/en_US/championFull.json"))["keys"]

    mastery_dict = {}
    entry_number = 0
    level_list = []
    total_points = 0
    total_champs = 0
    for entry in mastery_data:
        total_points += int(entry["championPoints"])
        total_champs += 1
        if entry_number <= 7:
            champName = champList[f"{entry['championId']}"]
            mastery_dict[champName] = int(entry["championPoints"])
            entry_number +=1
        if entry["championLevel"] >= 5:
            level_list.append(entry["championLevel"])

    print(mastery_dict)
    plt.style.use("dark_background")

    fig, ax = plt.subplots()
    fig.set_size_inches(5.41,3.5)
    ax.bar(list(mastery_dict.keys()), list(mastery_dict.values()), width=0.95, color="#6f9cde")
    print(list(mastery_dict.values()))

    def turn_to_k(x, pos):
        """The two args are the value and tick position"""
        return '{:1.0f}k'.format(x*1e-3)

    #ax.set(xlabel="Champion", ylabel="Points", title="Mastery Points for User: placeholder")
    ax.set_yticks(np.arange(0, list(mastery_dict.values())[0], step=20000))
    ax.yaxis.set_major_formatter(turn_to_k)
    ax.margins(x=0.025)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    #ax.spines['bottom'].set_visible(False)
    #ax.spines['left'].set_visible(False)

    #ax.set_ylim(0, list(mastery_dict.values())[0])
    plt.xticks(rotation=30, ha='right')

    # check if folder exists and create if not
    folder="src\\files\\SummonerMastery"
    if not path.isdir(folder):
        makedirs(folder, exist_ok=True)

    
    plt.savefig(f"{folder}\\{puuid}.png", bbox_inches='tight', pad_inches=0, transparent=True)

    img = Image.open(f"{folder}\\{puuid}.png")
    left = 0
    top = 10
    right = 464
    bottom = 320
    img_crop = img.crop((left, top, right, bottom))

    #img_rotate.show()
    img_crop.save(fp=f"{folder}\\{puuid}.png")
    return mastery_dict, total_points, total_champs, level_list


async def searchRune(searchQuery: str):
    """
    Parameters
    ----------
    searchQuery : str
        Name of rune to search; not sensitive to caps or spaces
    Returns
    -------
    found : bool
        True if found rune
    name : str
        Formatted rune name
    """
    


    runeList = f"http://ddragon.leagueoflegends.com/cdn/{await getLatestPatch()}/data/en_US/runesReforged.json"

    runeData = await getJSON(runeList)

    found = False
    name, description, icon, id_ = None, None, None, None
    for tree in runeData:
        for slot in tree["slots"]:
            for rune in slot["runes"]:
                if searchQuery.lower().replace(" ", "") == rune["key"].lower():
                    found = True
                    description = sub("<.*?>", "", rune["longDesc"].replace("<br>", "\n"))
                    name = rune["name"]
                    icon = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/{rune['icon'].lower()}"
                    id_ = rune["id"]
                    perk_tree = tree["name"]
                    perk_tree_icon = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/{tree['icon'].lower()}"
                    break
            else:
                continue
            break
        else:
            continue
        break

    return found, name, description, icon, id_, perk_tree, perk_tree_icon
