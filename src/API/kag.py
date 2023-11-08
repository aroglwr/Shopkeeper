from API.general import *
import random as r

async def getWebStatus():
    """ Returns various KAGstats API statuses
    
    Returns
    -------
    playerCount : int
        Amount of players tracked lifetime
    kills : int
        Amount of kills tracked lifetime
    serverCount : int
        Servers across which kills have been tracked
    apiVer : str
        Current version of KAGstats API
    """
    apiStatus = await getJSON("https://kagstats.com/api/status")

    playerCount = apiStatus["players"]
    kills = apiStatus["kills"]
    serverCount = apiStatus["servers"]
    apiVer = apiStatus["version"]

    return playerCount, kills, serverCount, apiVer

async def searchPlayer(playerName: str):
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

async def getPlayerList(playerIds):
    usernames = []
    for playerId in playerIds:
        data = run(getJSON(f"https://kagstats.com/api/players/{playerId}/basic"))
        usernames.append(data["player"]["charactername"])
    return usernames

async def getPlayerData(playerId: int):

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
        registered = data["player"]["registered"]
        return userExists, username, displayname, clantag, hasGold, avatar, killStats, url, registered
    except:
        return None

async def getServerList(official: bool):
    totalPlayers = 0
    if official:
        serverList = await (getJSON("https://kagstats.com/api/servers"))
        #steam://219830/
        servers = []
        for server in serverList:
            currentServer = getJSON_filter(f'https://api.kag2d.com/server/ip/{server["address"]}/port/{server["port"]}/status')["serverStatus"]
            print(f'https://api.kag2d.com/server/ip/{server["address"]}/port/{server["port"]}/status')
            if currentServer["currentPlayers"] != 0:
                players = currentServer["playerList"]
                playerList = []
                for player in players:
                    playerList.append(player["username"])
                servers.append([(currentServer["currentPlayers"], currentServer["maxPlayers"]), (currentServer["serverIPv4Address"], currentServer["serverPort"]), (currentServer["serverName"], currentServer["description"], currentServer["gameMode"]), playerList])
                
                totalPlayers += currentServer["currentPlayers"]
        servers.sort(key=lambda tup: tup[0], reverse=True)
    else:
        servers = []
        serverList = (await getJSON("https://api.kag2d.com/v1/game/thd/kag/servers?filters=[{%22field%22:%22current%22,%22op%22:%22eq%22,%22value%22:%22true%22},{%22field%22:%22connectable%22,%22op%22:%22eq%22,%22value%22:true}]&"))["serverList"]
        for server in serverList:
            if server["currentPlayers"] != 0:
                servers.append([(server["currentPlayers"], server["maxPlayers"]), (server["IPv4Address"], server["port"]), (server["name"], server["description"], server["gameMode"]), server["playerList"]])
                print(server["currentPlayers"])
                totalPlayers += server["currentPlayers"]
        servers.sort(key=lambda tup: tup[0], reverse=True)

    
    return servers, totalPlayers

async def getClanList():
    """ Gets list of clans sorted by kagstats (unknown sorting)

    Returns
    -------
        clans : list
            List of lists containing: clan name, clan creation date (epoch), ID of leader, member count, tuple of {leader username, leader display name, leader clantag}
    """
    clans = []
    clanList = await getJSON("https://kagstats.com/api/clans")
    for clan in clanList:
        clans.append([clan["name"], int(clan["createdAt"]/1000), clan["leaderID"], clan["membersCount"], (clan["leader"]["username"], clan["leader"]["charactername"], clan["leader"]["clantag"])])
    clans.sort(key=lambda x: x[3], reverse=True)

    return clans
async def searchClan(clanName: str):
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
    clanList = await getJSON("https://kagstats.com/api/clans")
    clanData = [False]
    for clan in clanList:
        if str(clan["name"]).lower() == clanName.lower():
            clanData[0] = True
            data = clan["name"], int(clan["createdAt"]/1000), clan["leaderID"], clan["membersCount"], clan["leader"]["username"], clan["leader"]["charactername"], clan["leader"]["clantag"], clan["id"]
            clanData.append(data)
            print(clanData)
    return clanData

async def getClanMembers(id: int):
    members = await getJSON(f"https://kagstats.com/api/clans/{id}/members")
    ids = []
    for member in members:
        ids.append(member["player"]["username"])
    return ids
