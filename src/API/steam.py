import discord
import math
from API.general import getJSON as getJSON
from API.general import getJSON_local as getJSON_local
from API.general import dateConvert

async def cacheGames():
    import json
    print("caching steam games")
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v1" # http://api.steampowered.com/ISteamApps/GetAppList/v0002
    gameList = await getJSON(url)
    with open("src\\files\\gameList.json", "w", encoding="utf-8") as f:
        json.dump(gameList, f, ensure_ascii=False, indent=4)
    print("games cached")

async def inputType(input):
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
    except:
        type = str  
    if type == int:
        appid = input
        return appid, True
    else:
        name = input
        return name, False

async def parseID(input):
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

    if (await inputType(input))[1] == True:
        print(input)
        return input

    else:
        output = await getID(input)
        return output
    


async def parseID_account(input, steam_token):
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
    input_type = await inputType(input)
    if input_type[1] == True:
        return input

    elif input_type[1] == False:
        getid = (await getJSON(f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={steam_token}&vanityurl={input}'))["response"]["steamid"]
        return getid
    else:
        print("error")
        pass



async def getPrice(appid):
    """ Gets the price of a game from the Steam API

    Parameters
    ----------
    appid : int
        Unique appid of a Steam Game

    Returns
    -------
    bool : bool
        Game has price or not    
    
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
    print(url)
    data = await getJSON(url)
    
    try:
        overview = data[f'{appid}']["data"]["price_overview"]
        price_initial = overview["initial"]
        price_final = overview["final"]
        price_formatted = overview["final_formatted"]
        price_formatted_before = overview["initial_formatted"]
        currency = overview["currency"]
        discount = overview["discount_percent"]
        return True, price_initial, price_final, price_formatted, currency, discount, price_formatted_before
    except:
        return False

async def gameData(appid: int):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=eng"
    print(url)
    data = (await getJSON(url))[f"{appid}"]["data"]
    info = (data["name"], data["short_description"], data["developers"], data["publishers"], data["release_date"])
    images = (data["header_image"], data["capsule_image"])
    genreList = data["genres"]
    genres=[]
    for genre in genreList:
        genres.append(genre["description"])
    try:
        priceData = data["price_overview"] 
        priceData = [True, priceData["initial"], priceData["final"], priceData["final_formatted"], priceData["initial_formatted"], priceData["currency"], priceData["discount_percent"]]
    except:
        priceData = [False]
    
    
    return info, images, genres, priceData



async def getName(appid):

    # Set up JSON read

    url = f'https://store.steampowered.com/api/appdetails?appids={appid}'
    data = await getJSON(url)
    return data[str(appid)]["data"]["name"]



async def getID(input):
    # Set up JSON read
    url = 'src\\files\\gameList.json'
    data = await getJSON_local(url)
    
    apps = data["applist"]["apps"]["app"]
    # Just check
    #print("Searching for name...")

    for app in apps:
        if str(app["name"]).lower() == str(input).lower():
            appid = app["appid"]
            return appid

        #print("error getting id")





async def accountInfo(steam_token, userid_input):
    """
    """
    userid = await parseID_account(userid_input, steam_token)
    userData = (await getJSON(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={steam_token}&format=json&steamids={userid}'))["response"]["players"][0]
    print(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={steam_token}&format=json&steamids={userid}')
    print(f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_token}&steamid={userid}&format=json')
    isPrivate = userData["communityvisibilitystate"]
    
    if isPrivate == 3:
        userGames = (await getJSON(f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_token}&steamid={userid}&format=json'))["response"]
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
        except:
            inGame = ""
        
        playtime = 0
        for i in range(gamesCount):
            playtime += gamesList[i]["playtime_forever"]
        rounded_ptime = round(playtime/60)
        username = userData["personaname"]
        creationDate = dateConvert(userData["timecreated"])[3]
        #lastLogoff = dateConvert(userData["lastlogoff"])[2]
        lastLogoff = userData["lastlogoff"]
        return isPrivate, username, creationDate, rounded_ptime, profilePicture, profileRegion, gamesCount, (player_status, inGame), profileURL, profilePicture_small, lastLogoff
    
    else:
        return isPrivate, ""

async def accountBans(steam_token, userid_input):
    """
    """
    userid = await parseID_account(userid_input, steam_token)
    userbans = (await getJSON(f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={steam_token}&steamids={userid}'))["players"][0]
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

async def achievementInfo(steam_token, userid_input, appid_input):
    """
    """
    appid = await parseID(appid_input)
    userid = await parseID_account(userid_input, steam_token)
    achieve_json = (await getJSON(f'http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={steam_token}&steamid={userid}'))["playerstats"]
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


























































def detailOutput(input):
    """ THIS IS A LEGACY FUNCTION - Generates game details based on ID

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
    """ THIS IS A LEGACY FUNCTION - Creates an embed for Discord.py

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