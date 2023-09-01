from API.general import getJSON_filter
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

def getServerList():
    servers = getJSON_filter("https://kagstats.com/api/servers")
    #steam://219830/
    onlineServers = []
    for i in range(len(servers)):
        if servers[i]["status"] == True:
            onlineServers.append(servers[i])

    return onlineServers[0]




