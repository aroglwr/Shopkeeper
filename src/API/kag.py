from API.general import *
import random as r

def getWebStatus():
    apiStatus = getJSON_filter("https://kagstats.com/api/status")

    playerCount = apiStatus["players"]
    kills = apiStatus["kills"]
    serverCount = apiStatus["servers"]
    apiVer = apiStatus["version"]

    return playerCount, kills, serverCount, apiVer

def searchPlayer(playerName):
    blank = playerName.find(" ")
    if blank == -1:
        playerName_f = playerName
    else:
        playerName_f = playerName[:blank]
    try:

        result = getJSON_filter(f'https://kagstats.com/api/players/search/{playerName_f.lower()}')[0]
        return result["id"]
    except:
        pass

def getPlayerData(playerId):

    try:
        data = getJSON_filter(f'https://kagstats.com/api/players/{playerId}/basic')
        userExists = True
        username = data["player"]["username"]
        displayname = data["player"]["charactername"]
        clantag = data["player"]["clantag"]
        hasGold = data["player"]["oldGold"]
        avatar = data["player"]["avatar"] # can be = ""
        if avatar == "":
            avatar = f'https://kagstats.com/assets/portrait{r.randint(1,3)}.png'
        killStats = [data["suicides"], data["teamKills"], [data["archerKills"], data["archerDeaths"]], [data["builderKills"], data["builderDeaths"]], [data["knightKills"], data["knightDeaths"]], [data["totalKills"], data["totalDeaths"]]]
        url = f"https://kagstats.com/#/players/{playerId}"
        return userExists, username, displayname, clantag, hasGold, avatar, killStats, url
    except:
        return None

def getServerList(official: bool):
    totalPlayers = 0
    if official:
        serverList = getJSON("https://kagstats.com/api/servers")
        #steam://219830/
        servers = []
        for server in serverList:
            currentServer = getJSON_filter(f'https://api.kag2d.com/server/ip/{server["address"]}/port/{server["port"]}/status')["serverStatus"]
            if currentServer["currentPlayers"] != 0:
                servers.append([currentServer["currentPlayers"], (currentServer["serverIPv4Address"], currentServer["serverPort"]), (currentServer["serverName"], currentServer["description"])])
                totalPlayers += currentServer["currentPlayers"]
        servers.sort(key=lambda tup: tup[0], reverse=True)
    else:
        servers = []
        serverList = getJSON("https://api.kag2d.com/v1/game/thd/kag/servers?filters=[{%22field%22:%22current%22,%22op%22:%22eq%22,%22value%22:%22true%22},{%22field%22:%22connectable%22,%22op%22:%22eq%22,%22value%22:true}]&")["serverList"]
        for server in serverList:
            if server["currentPlayers"] != 0:
                servers.append([server["currentPlayers"], (server["IPv4Address"], server["port"]), (server["name"], server["description"])])
                totalPlayers += server["currentPlayers"]
        servers.sort(key=lambda tup: tup[0], reverse=True)

    
    return servers, totalPlayers

def getClanList():
    """ Gets list of clans sorted by kagstats (unknown sorting)

    Returns
    -------
        clans : list
            List of lists containing: clan name, clan creation date (epoch), ID of leader, member count, tuple of {leader username, leader display name, leader clantag}
    """
    clans = []
    clanList = getJSON("https://kagstats.com/api/clans")
    for clan in clanList:
        clans.append([clan["name"], clan["createdAt"], clan["leaderID"], clan["membersCount"], (clan["leader"]["username"], clan["leader"]["charactername"], clan["leader"]["clantag"])])

    return clans
def searchClan(clanName: str):
    """ Searches for specific clan name on kagstats API

    Parameters
    ----------
    clanName : str
        Name of clan to search (not case sensitive)
    
    Returns
    -------
        clanData : list
            At respective address contains: clan name, clan creation date (epoch), ID of leader, member count, leader username, leader display name, leader clantag
    """
    clanList = getJSON("https://kagstats.com/api/clans")
    clanData = [False]
    for clan in clanList:
        if str(clan["name"]).lower() == clanName.lower():
            clanData[0] = True
            data = clan["name"], clan["createdAt"], clan["leaderID"], clan["membersCount"], clan["leader"]["username"], clan["leader"]["charactername"], clan["leader"]["clantag"]
            clanData.append(data)
    return clanData


