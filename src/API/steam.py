import discord
import math
from API.general import getJSON as getJSON
from API.general import getJSON_local as getJSON_local
from API.general import dateConvert


def inputType(input):
    """ Determines input type and returns it

    Parameters
    ----------
    input : undetermined form
        User input 
    
    Returns
    -------
    name or appid : int / str
        Either 
    
    bool : bool
        True for int false for non-int
    """
    try:
        input = int(input)
        type = int
    except ValueError as ve:
        type = str  
    if type == int:
        appid = input
        return appid, True
    else:
        name = input
        return name, False

def parseID(input):
    """ Parses input and returns ID if name or ID is inputted

    Parameters
    ----------
    input : undetermined form
        User input 
    
    Returns
    -------
    name or appid : int / str
        Either 
    
    output : ID of game inputted
        True for int false for non-int
    """
    if inputType(input)[1] == True:
        return input

    elif inputType(input)[1] == False:
        output = getID(input)
        return output
    else:
        print("error")
        pass


def parseID_account(input, steam_token):
    """ Parses input and returns ID if name or ID is inputted

    Parameters
    ----------
    input : undetermined form
        User input 

    steam_token : str
        Steam token
    Returns
    -------
    name or appid : int / str
        Either 
    
    output : ID of game inputted
        True for int false for non-int
    """
    
    if inputType(input)[1] == True:
        return input

    elif inputType(input)[1] == False:
        getid = getJSON(f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={steam_token}&vanityurl={input}')["response"]["steamid"]
        return getid
    else:
        print("error")
        pass



def getPrice(appid):
    """ Gets the price of a game from the Steam API

    Parameters
    ----------
    appid : int
        Unique appid of a Steam Game

    Returns
    -------
    price_initial : int
        Price of game in GBP

    price_final : int
        Price of game after sale in GBP

    price_formatted : str
        Price formatted with currency and decimals

    currency : str
        Game price currency e.g. GBP

    discount : int
        Discount on game sale as percentage
    """
    url = f'https://store.steampowered.com/api/appdetails?filters=price_overview&appids={appid}'
    data = getJSON(url)
    
    login = data[f'{appid}']["success"]
    overview = data[f'{appid}']["data"]["price_overview"]
    if login == True:
        price_initial = overview["initial"]
        price_final = overview["final"]
        price_formatted = overview["final_formatted"]
        price_formatted_before = overview["initial_formatted"]
        currency = overview["currency"]
        discount = overview["discount_percent"]
        return price_initial, price_final, price_formatted, currency, discount, price_formatted_before
    else:
        return None

def getName(appid):

    # Set up JSON read
    url = f'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
    data = getJSON(url)
    appid = appid
    apps = data["applist"]["apps"]
    # Just check
    #print("Searching for name...")
    
    for i in range(len(apps)):
        if apps[i]["appid"] == int(appid):
            name = apps[i]["name"]
    return name


def getID(input):

    # Set up JSON read
    url = f'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
    data = getJSON(url)
    apps = data["applist"]["apps"]
    # Just check
    #print("Searching for name...")
    appid = []
    try:
        for i in range(len(apps)):
            if apps[i]["name"] == str(input):
                appid = apps[i]["appid"]
        return appid
    except:
        print("Error")



def detailOutput(input):
    """ Generates game details based on ID

    Parameters
    ----------
    input : int
        Unique appid of a Steam Game

    Returns
    -------
    price : Price of game with appid
        Price of game in GBP
    """
    appid = parseID(input)
    p = getPrice(appid)
    if p[4] != 0:
        output = f'{getName(appid)} with appid: {appid} is on sale\n'
        output += f'It is {p[2]}\n'
        output += f'It is {p[4]}% on sale!'

    else:
        output = f'{getName(appid)} with appid: {appid} is not on sale\nIt is {p[2]} {p[3]}'

    return output

def embedOutput(input):
    """ Creates an embed for Discord.py

    Parameters
    ----------
    input : str
        AppID or Name of Steam game

    Returns
    -------
    embed
    """
    appid = parseID(input)
    p = getPrice(appid)
    
    image = f'https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/hero_capsule.jpg'
    gameName = getName(appid)
    gameNameURL = gameName.replace(" ","_")
    store_page = f'https://store.steampowered.com/app/{appid}/{gameNameURL}'

    description_text = f'Is {p[2]} {p[3]}'
    if p[4] != 0:
        description_text += f' and is {p[4]}% on sale!'
    else:
        pass
    embed=discord.Embed(title=f'{gameName} ({appid})', url=store_page, description=description_text, color=0x0080ff)

    embed.set_author(name="aroglwr#2687", icon_url="https://cdn.discordapp.com/avatars/231836257334984704/71e9091e3f10aa1956fb7eba5bc677e6.webp")
    embed.set_thumbnail(url=image)
    if p[4] != 0:
        embed.add_field(name="Price Before", value=p[5], inline=True)
        embed.add_field(name="Price After", value=p[2], inline=True)
    else:
        embed.add_field(name=f'This is so sad', value=":sob: literally me")
    
    return embed


def accountInfo(steam_token, userid_input):
    """
    """
    userid = parseID_account(userid_input, steam_token)
    userData = getJSON(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={steam_token}&format=json&steamids={userid}')["response"]["players"][0]

    isPrivate = userData["communityvisibilitystate"]
    
    if isPrivate == 3:
        userGames = getJSON(f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_token}&steamid={userid}&format=json')["response"]
        gamesList = userGames["games"]
        gamesCount = userGames["game_count"]
        profilePicture = userData["avatarfull"]
        profilePicture_small = userData["avatar"]
        try:
            profileRegion = userData["loccountrycode"]
        except:
            profileRegion = ""
        profileURL = userData["profileurl"]
        player_status = userData["personastate"]
        try:
            inGame = userData["gameextrainfo"]
            onlineStatus = f'is playing {inGame}'
        except:
            if player_status == 1:
                onlineStatus = f'is online.'
            elif player_status == 0:
                onlineStatus = f'is offline.'
        
        playtime = 0
        for i in range(gamesCount):
            playtime += gamesList[i]["playtime_forever"]
        rounded_ptime = round(playtime/60)
        username = userData["personaname"]
        creationDate = dateConvert(userData["timecreated"])[3]
        #lastLogoff = dateConvert(userData["lastlogoff"])[2]
        return isPrivate, username, creationDate, rounded_ptime, profilePicture, profileRegion, gamesCount, onlineStatus, profileURL, profilePicture_small
    
    else:
        return isPrivate, ""

def accountBans(steam_token, userid_input):
    """
    """
    userid = parseID_account(userid_input, steam_token)
    userbans = getJSON(f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={steam_token}&steamids={userid}')["players"][0]
    if userbans["CommunityBanned"] == False:
        communityban = "No"
    else:
        communityban = "Yes"
    if userbans["EconomyBan"] == "none":
        economyban = "No"
    else:
        economyban = "Yes"
    if userbans["VACBanned"] == False:
        vacban = "None"
    else:
        vacban_no = userbans["NumberOfVACBans"]
        vacban = f'{vacban_no} bans'
    if userbans["NumberOfGameBans"] == 0:
        gamebans = "None"
    else:
        gamebans = f'{userbans["NumberOfGameBans"]} bans'
    return communityban, economyban, vacban, gamebans

def achievementInfo(steam_token, userid_input, appid_input):
    """
    """
    appid = parseID(appid_input)
    userid = parseID_account(userid_input, steam_token)
    achieve_json = getJSON(f'http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={steam_token}&steamid={userid}')["playerstats"]
    achieve_list = achieve_json["achievements"]

    if achieve_json["success"] == True:
        achieve_count = 0
        rq_success = 1
        achieve_total = len(achieve_list)
        for i in range(achieve_total):
            if achieve_list[i]["achieved"] == 1:
                achieve_count += 1
            else:
                achieve_count += 0
        achieve_percentage = math.floor((achieve_count/len(achieve_list)) * 100)
    elif achieve_json["success"] == False:
        rq_success = 0

    
    return rq_success, achieve_count, achieve_percentage, achieve_total



