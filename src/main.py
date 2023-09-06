import discord
from discord import app_commands
from discord.ext import tasks
import API.general as general
import API.steam as steam
import API.league as league
import API.kag as kag
import time, datetime
#import API.hypixel as hp
import random


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
aroglwr_image = client.fetch_user(231836257334984704)

prefix = "!"
changeStatus = False
cfg = general.getJSON_local("src/config.json")
steam_token = cfg["steam_token"]
riot_token = cfg["riot_token"]
summonerEmoji = cfg["riot"]["leagueSummonerSpells"]
runeEmoji = cfg["riot"]["leagueRunes"]
startTime = time.time()

"""

class hypixel(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="Bedwars",description="This is option 1!"),
            discord.SelectOption(label="Wool Wars",description="This is option 2!"),
            discord.SelectOption(label="TNT Games",description="This is option 3!")
            ]
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):
        
        if self.values[0] == "Bedwars":

            embed=discord.Embed(title=f'bedwars', url=f'', description=f'{hp.dummy(self.values[0])}', color=0x0000ff)
        
            disp_name = str(client.user)[:-5] + " bot"
            embed.set_footer(text=f'{disp_name}')
            await interaction.response.edit_message(embed=embed)
        elif self.values[0] == "Wool Wars":
            embed=discord.Embed(title=f'wool wars', url=f'', description=f'{hp.dummy(self.values[0])}', color=0x0000ff)

            disp_name = str(client.user)[:-5] + " bot"
            embed.set_footer(text=f'{disp_name}')
            await interaction.response.edit_message(embed=embed)
        elif self.values[0] == "TNT Games":
            embed=discord.Embed(title=f'tnt games', url=f'', description=f'{hp.dummy(self.values[0])}', color=0x0000ff)

            disp_name = str(client.user)[:-5] + " bot"
            embed.set_footer(text=f'{disp_name}')
            await interaction.response.edit_message(embed=embed)

class hypixelView(discord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout=timeout)
        self.add_item(hypixel())
"""


@client.event
async def on_ready():
    await tree.sync()
    # Start the task
    status_loop.start()
    print(f'We have logged in as {client.user}')

# Generic Commands
@tree.command(name = "gif", description = "Funny gif generator")
async def gif(interaction: discord.Interaction):
    await interaction.response.defer()
    gifList = cfg["gifs"]
    gifOut = gifList[random.randint(0,len(gifList)-1)] 
    await interaction.followup.send(gifOut)
    #await interaction.response.send_message(gifOut)
@tree.command(name = "crunch", description = "Crunch!")
async def crunch(interaction: discord.Interaction):
    await interaction.response.defer()
    gifList = cfg["crunch"]
    gifOut = gifList[random.randint(0,len(gifList)-1)]
    await interaction.followup.send(gifOut)

    #await interaction.response.send_message(gifOut)
@tree.command(name = "about", description = f"About {str(client.user)[:-5]}")
async def about(interaction: discord.Interaction):
    """about description
    """
    await interaction.response.defer(ephemeral=True)
    uptime = str(datetime.timedelta(seconds=int(round(time.time()-startTime))))
    pythonVer, discordVer, kagVer = [general.getVersion(), f"{discord.version_info[0]}.{discord.version_info[1]}.{discord.version_info[2]}", kag.getWebStatus()[3]]
    
    # stats
    guilds = client.guilds
    memberCount = 0
    for guild in guilds:
        for member in guild.members:
            if not member.bot:
                memberCount += 1

    serverCount, userCount = [str(len(guilds)), memberCount]
    embed=discord.Embed(title=f'View on GitHub', url=f'https://github.com/aroglwr', description=f'', color=0x0000ff)
    embed.add_field(name=f"About {client.user.display_name}", value=f"{serverCount} servers with {userCount} users", inline=False)

    embed.add_field(name="Python", value=f"[{pythonVer}](https://www.python.org/)")
    embed.add_field(name="discord.py", value=f"[{discordVer}](https://discordpy.readthedocs.io/en/stable/)")
    embed.add_field(name="KAGstats", value=f"[{kagVer}](https://kagstats.com)")
    embed.add_field(name = "test", value = "```\ntest \n test1```", inline=False)


    embed.set_author(name=f'Uptime: {uptime}', icon_url=client.user.display_avatar.url)
    #embed.set_thumbnail(url=client.user.display_avatar.url)

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')

    await interaction.followup.send(embed=embed)

# Steam Commands
@tree.command(name = "steamgameinfo", description = "Gets game data from Steam website")
async def gameid(interaction: discord.Interaction, name_or_id: str):
    await interaction.response.defer()
    appid = steam.parseID(name_or_id)
    p = steam.getPrice(appid)
    
    image = f'https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/hero_capsule.jpg'
    gameName = steam.getName(appid)
    gameNameURL = gameName.replace(" ","_")
    store_page = f'https://store.steampowered.com/app/{appid}/{gameNameURL}'

    description_text = f'Is {p[2]} {p[3]}'
    if p[4] != 0:
        description_text += f' and is {p[4]}% on sale!'
    else:
        pass
    embed=discord.Embed(title=f'Store Page', url=store_page, description=description_text, color=0x1a1aff)

    embed.set_author(name=f'{gameName} ({appid})', icon_url=f'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/800px-Steam_icon_logo.svg.png')
    embed.set_thumbnail(url=image)
    if p[4] != 0:
        embed.add_field(name="Price Before", value=p[5])
        embed.add_field(name="Price After", value=p[2])
    else:
        embed.add_field(name=f'This is so sad', value=":sob: literally me")

    players_online = steam.getJSON(f'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key={steam_token}&appid={appid}')["response"]["player_count"]
    embed.add_field(name=f'Players Online', value=f'{players_online}')
    disp_name = str(client.user)[:-5] + " bot"

    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "steamuserinfo", description = "Gets user data from Steam website")
async def steamuserinfo(interaction: discord.Interaction, name: str):
    """steamuserinfo description

    Args:
        name (str): Vanity URL or profile ID
    """
    await interaction.response.defer()
    
    try:
        info = steam.accountInfo(steam_token, name)
        bans = steam.accountBans(steam_token, name)
        if info[0] == 3:
            profileImage = info[4]
            profileImage_small = info[9]
            name = info[1]
            
            region = info[5]
            if region == "":
                region= "No Region"
            accountDate = info[2]
            gameCount = info[6]
            playtime = info[3]
            profile_url = info[8]
            online_status = info[7]
            embed=discord.Embed(title=f'Profile Link', url=profile_url, description=f'{name} {online_status}', color=0x0080ff)
            embed.set_author(name=f'{name} ({region})', icon_url=f'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/800px-Steam_icon_logo.svg.png')
            embed.add_field(name="Account Created", value=accountDate)
            embed.add_field(name="Game Library", value=f'{gameCount} games')
            embed.add_field(name="Total Playtime", value=f'{playtime} hours')
            embed.add_field(name="VAC Bans?", value=f'{bans[2]}')
            embed.add_field(name="Community Ban?", value=f'{bans[0]}')
            embed.add_field(name="Trade Ban?", value=f'{bans[1]}')
            embed.set_thumbnail(url=profileImage)
        else:
            embed=discord.Embed(title=f'', description=f'', color=0x0080ff)
            embed.set_author(name=f'User profile is private', icon_url=f'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/800px-Steam_icon_logo.svg.png')
    except:
        embed=discord.Embed(title=f'', description=f'', color=0x0080ff)
        embed.set_author(name=f'Could not find user', icon_url=f'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/800px-Steam_icon_logo.svg.png')
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "steamachievementinfo", description = "Get a user's Steam achievement data for a game")
async def achievements(interaction: discord.Interaction, username: str, name_or_id: str):
    await interaction.response.defer()
    appid = steam.parseID(name_or_id)
    image = f'https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/hero_capsule.jpg'
    gameName = steam.getName(appid)
    store_page = f'https://store.steampowered.com/app/{appid}/{gameName.replace(" ","_")}'
    achievement_info = steam.achievementInfo(steam_token, username, name_or_id)
    info = steam.accountInfo(steam_token, username)
    
    embed=discord.Embed(title=f"Stats for {gameName}", url=store_page, description=f'{info[1]} has {achievement_info[1]}/{achievement_info[3]} ({achievement_info[2]}%) achievements for {gameName}', color=0x0000ff)
    embed.set_author(name=f'{info[0]}', icon_url=f'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/800px-Steam_icon_logo.svg.png')
    embed.set_thumbnail(url=image)
    
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    
    #messageOut = f'Steam user {steam.accountInfo(steam_token, userid_input)[0]} for game {appid_name}\nHas {achievement_info[2]}% completion.'
    #print(messageOut)
    await interaction.followup.send(embed=embed)

# League Commands
@tree.command(name = "masterysearch", description = "Search a League of Legends summoner's mastery data by champion")
async def masterysearch(interaction: discord.Interaction, summoner_name: str, region: str, champion: str):
    await interaction.response.defer()
    summoner_data = league.getSummonerData(summoner_name, region, riot_token)
    masterySearch = league.masterySearch(summoner_data[5], champion, riot_token, region)
    if masterySearch[4] >= 4:
        image = f'https://raw.communitydragon.org/latest/game/assets/ux/mastery/mastery_icon_{masterySearch[4]}.png'
    else:
        image = "https://raw.communitydragon.org/latest/game/assets/ux/mastery/mastery_icon_default.png"
    
    embed=discord.Embed(title=f'ChampionMastery.GG', url=f'https://championmastery.gg/summoner?summoner={summoner_data[6]}&region={region.upper()}&lang=en_US', description=f'{league.getChampionName(masterySearch[3])} with {masterySearch[0]:,} at level {masterySearch[4]}', color=0x0000ff)
    embed.add_field(name=f"Chest Earned?", value=f"{masterySearch[1]}")
    embed.add_field(name="Progress", value=f'{masterySearch[2]}')
    embed.set_author(name=f'{summoner_data[0]} ({region.upper()})', icon_url=image)
    embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{masterySearch[3]}.png')

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "highestmastery", description = "Displays user's highest League of Legends champion mastery")
async def highestmastery(interaction: discord.Interaction, summoner_name: str, region: str):
    await interaction.response.defer()

    summoner_data = league.getSummonerData(summoner_name, region, riot_token)
    highestMastery = league.highestMasteryData(summoner_data[5], riot_token, region)
    if highestMastery[4] >= 4:
        image = f'https://raw.communitydragon.org/latest/game/assets/ux/mastery/mastery_icon_{highestMastery[4]}.png'
    else:
        image = "https://raw.communitydragon.org/latest/game/assets/ux/mastery/mastery_icon_default.png"

    embed=discord.Embed(title=f'ChampionMastery.GG', url=f'https://championmastery.gg/summoner?summoner={summoner_data[6]}&region={region.upper()}&lang=en_US', description=f'{league.getChampionName(highestMastery[3])} with {highestMastery[0]:,} at level {highestMastery[4]}', color=0x0000ff)
    embed.add_field(name=f"Chest Earned?", value=f"{highestMastery[1]}")
    embed.add_field(name="Progress", value=f'{highestMastery[2]}')
    embed.set_author(name=f'{summoner_data[0]} ({region.upper()})', icon_url=image)
    embed.set_thumbnail(url=f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{highestMastery[3]}.png")

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "match_history", description = "Displays user's League of Legends match history")
async def matchhistory(interaction: discord.Interaction, summoner_name: str, region: str):
    """matchhistory description

    Args:
        summoner_name (str): Name of summoner
        region(str): Where that summoner is registered in e.g. euw, na, kr
    """
    await interaction.response.defer()

    # Loading panel
    embed_load=discord.Embed(title=f'', description=f'Please wait', color=0x00afff)
    embed_load.set_author(name=f'Searching Match History', icon_url="https://i.gifer.com/ZKZg.gif")
    update = await interaction.followup.send(embed=embed_load)
    
    summonerData =  league.getSummonerData(summoner_name, region, riot_token)
    matchData = league.getMatchHistory(riot_token, summonerData[1], region, 5)
    rankedData = league.getRankedData(riot_token, summonerData[5], region)
    print(rankedData)
    
    if matchData[0] == True:
        if rankedData[0] == True:
            hasRank, rankIcon, rankedQueue, rankedTier, rank,  rankedWins, rankedLosses, leaguePoints = rankedData
            if rankedLosses != 0:
                winRate = (rankedWins/(rankedLosses + rankedWins)) * 100
            else:
                winRate = 100
                print(rankedWins)
            if rankedTier not in ("CHALLENGER", "GRANDMASTER", "MASTER"):
                if leaguePoints < 100:
                
                    promoStatus = f"{int(leaguePoints)}% to promotion"
                else:
                    promoStatus = "Promoted!"
            else:
                promoStatus = ""
            embed=discord.Embed(title=f'View on OP.GG', url=f'https://www.op.gg/summoners/{region}/{summonerData[6]}', description=f'{summonerData[0]} has {round(winRate, 2)}% WR in {rankedQueue} and is {rankedTier.capitalize()} {rank} {leaguePoints} LP', color=0x0000ff)
            embed.add_field(name="Progress to Promotion", value=f"`{general.progressBar(20, leaguePoints/100)}` {promoStatus}", inline=False)
            embed.set_author(name=f'{summonerData[0]} ({region.upper()}) - {rankedWins}W/{rankedLosses}L', icon_url=rankIcon)
        else:
            rankIcon = rankedData [1]
            embed=discord.Embed(title=f'View on OP.GG', url=f'https://www.op.gg/summoners/{region}/{summonerData[6]}', description=f'No ranked data for {summonerData[0]}', color=0x0000ff)
            embed.set_author(name=f'{summonerData[0]} ({region.upper()})', icon_url=rankIcon)
        champName, win, role, gameType = matchData[1]
        
        
        embed.set_thumbnail(url=league.getSummonerIcon(summonerData[3]))

        for i in range(len(win)):
            embed.add_field(name="W/L", value=f'{win[i]}')
            embed.add_field(name="Gamemode", value=f'{gameType[i]}')
            if role[i] != "Invalid":
                embed.add_field(name="Champion", value=f'{champName[i]} {role[i]}')
            else:
                embed.add_field(name="Champion", value=f'{champName[i]}')
    else:
        embed=discord.Embed(title="Could not load match history", description='', color=0x0000ff)
        embed.set_thumbnail(url="https://static.wikia.nocookie.net/leagueoflegends/images/c/c0/LoL_ping_missing.png")
        

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')

    # Send the embed update
    update= await update.edit(embed=embed)

@tree.command(name = "championdata", description="Gets data for a League of Legends champion")
async def championdata(interaction: discord.Interaction, champion_name: str):
    await interaction.response.defer()
    try:
        championData = league.getChampionData(champion_name)

        embed=discord.Embed(title=f'Data for {championData[0]} {championData[1]}', description=f'{championData[2]}', color=0xff7518)
        embed.add_field(name="Skins", value=f"[Click to View](https://teemo.gg/viewer/league-of-legends/champions/{championData[10]}/0): " + general.unpackList(championData[9][1:], True), inline=False)
        embed.add_field(name="Spells", value="", inline=False)
        embed.add_field(name="Tags", value=f'{championData[5]}')
        embed.add_field(name="Resource Bar", value=f'{championData[7]}')
        #embed.set_image(url=championData[3])
        if championData[8] != None:
            embed.add_field(name="Tip", value=f'{str(championData[8])}')
        embed.set_thumbnail(url=championData[3])
    except:
        embed=discord.Embed(title=f"Could Not Find Champion \"{champion_name}\"", color=0xff7518)
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "itemdata", description="Gets data for a League of Legends item")
async def itemdata(interaction: discord.Interaction, item_name: str):
    await interaction.response.defer()
    try:
        itemData = league.getItemData(item_name)
        embed=discord.Embed(title=f'Data for {itemData[3]}', description=f'{itemData[2]}.', color=0xff7518)
        embed.add_field(name="Cost", value=f"{itemData[1]} <:gold:1148709055087521883>")
        embed.add_field(name="Combine Cost", value=f"{itemData[6]} <:gold:1148709055087521883>")
        embed.add_field(name="Sell Value", value=f"{itemData[7]} <:gold:1148709055087521883>")
        print(general.unpackList(itemData[4], True))
        print(general.unpackList(itemData[5], True))
        if itemData[4] != []:
            embed.add_field(name="Build Path", value=general.unpackList(itemData[4], True))
        if itemData[5] != []:
            embed.add_field(name="Builds Into", value=general.unpackList(itemData[5], True))
        #embed.set_image(url=championData[3])
        embed.set_thumbnail(url=itemData[0])
    except:
        embed=discord.Embed(title=f"Could Not Find Item \"{item_name}\"", color=0xff7518)
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "weeklyrotation", description = "Gets League of Legends champions which are on the weekly rotation")
async def weeklyrotation(interaction: discord.Interaction):
    await interaction.response.defer()

    
    embed=discord.Embed(title="This weeks champion rotation", description=f'{general.unpackList(league.getWeeklyRotation(riot_token), True)}', color=0x0000ff)

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "leaguelivegame", description = "Gets live game data for a League of Legends player")
async def leaguelivegame(interaction: discord.Interaction, summoner_name: str, region: str):
    """leaguelivegame description

    Args:
        summoner_name (str): Name of summoner
        region(str): Where that summoner is registered in e.g. euw, na, kr
    """
    await interaction.response.defer()

    # Loading panel
    embed_load=discord.Embed(title=f'', description=f'Please wait', color=0x00afff)
    embed_load.set_author(name=f'Fetching Live Game Info', icon_url="https://i.gifer.com/ZKZg.gif")
    update = await interaction.followup.send(embed=embed_load)

    summoner_data = league.getSummonerData(summoner_name, region, riot_token)
    liveGameData = league.getLiveGame(riot_token, summoner_data[5], region, summonerEmoji, runeEmoji)    


    if liveGameData[0] == True:
        embed=discord.Embed(title=f'View on OP.GG (Spectate)', url=f'https://www.op.gg/summoners/{region}/{summoner_data[6]}/ingame', description=f'{summoner_data[0]} is playing {liveGameData[3]} in {liveGameData[2][1]} on {liveGameData[2][0]}\nSummoner has been in game for {liveGameData[7][0]} minutes {liveGameData[7][1]} seconds', color=0x0000ff)
        #primaryTree = liveGameData[8][1][:4]
        #secondaryTree = general.unpackList(liveGameData[8][1][4:6])
        runeEmojis = liveGameData[8]
        embed.add_field(name="Spells", value=f'{liveGameData[6][0]} {liveGameData[6][1]}')
        embed.add_field(name="Runes", value=f'{runeEmojis[0]} {runeEmojis[1]} {runeEmojis[2]}{runeEmojis[3]}\n{runeEmojis[4]} {runeEmojis[5]}')
        #embed.add_field(name="Banned Champions", value=f'{general.unpackList(liveGameData[4][0], True) + general.unpackList(liveGameData[4][1], True)}', inline=False)
        embed.add_field(name="Banned Champions", value=f'{general.unpackList(liveGameData[4][0] + liveGameData[4][1], True)}', inline=False)
        embed.add_field(name="", value=f'')
        embed.add_field(name="", value=f'')

        embed.set_author(name=f'{summoner_data[0]} ({region.upper()})', icon_url=league.getSummonerIcon(summoner_data[3]))
        embed.set_thumbnail(url=liveGameData[5])
        
        
    
    else:
        embed=discord.Embed(title="Summoner is not in game", description='', color=0x0000ff)
        embed.set_thumbnail(url="https://static.wikia.nocookie.net/leagueoflegends/images/c/c0/LoL_ping_missing.png")
    

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    #await interaction.followup.send(embed=embed)
    # Send the embed update
    update= await update.edit(embed=embed)
    

@tree.command(name = "gameanalysis", description= "Gets an analysis of a single League of Legends game")
async def gameanalysis(interaction: discord.Interaction, summoner_name: str, region: str, game_number: int):
    """gameanalysis description

    Args:
        summoner_name (str): Name of summoner
        region(str): Where that summoner is registered in e.g. euw, na, kr
        game_number (int): Game number starting from most recent e.g. most recent is 1
    """
    await interaction.response.defer()
    # Loading panel
    #embed_load=discord.Embed(title=f'', description=f'Please wait', color=0x00afff)
    #embed_load.set_author(name=f'Analysing Game', icon_url="https://i.gifer.com/ZKZg.gif")
    #update = await interaction.followup.send(file=file, embed=embed_load)


    summonerData =  league.getSummonerData(summoner_name, region, riot_token)
    match_history = league.getMatchHistory(riot_token, summonerData[1], region, game_number)
    match_id= match_history[2][0][game_number-1]
    
    region_f = match_history[2][1]
    mapType = match_history[1][3][game_number-1]
    

    league.drawMap(riot_token, match_id, region_f, mapType) # https://europe.api.riotgames.com/lol/match/v5/matches/EUW1_6579462123/timeline?api_key=RGAPI-b560a406-267a-4dfe-b7a8-c14b5c6f2a50
    file = discord.File(f"src/files/LeagueMaps/{match_id[:2]}/{match_id}.png", filename="map.png")

    embed = discord.Embed(title="game analysis", description="this command is incomplete")
    embed.set_image(url="attachment://map.png")



    
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    #await interaction.followup.send(embed=embed)
    # Send the embed update
    await interaction.followup.send(file=file, embed=embed)

# KAG Commands
@tree.command(name = "kagstats", description="Gets King Arthur's Gold Stats for a player")
async def kagstats(interaction: discord.Interaction, name: str):
    """kagstats description

    Args:
        name (str): Name of user to search for
    """
    await interaction.response.defer()

    apiData = kag.getWebStatus()
    playerData = kag.getPlayerData(kag.searchPlayer(name))

    if playerData is not None and playerData[0] == True:
        #killData = kag.getPlayerStats(playerData[6])
        suicides, teamKills, archerStats, builderStats, knightStats, totalStats = playerData[6]
        if archerStats[0] != 0:
            archerKda = round(archerStats[0]/archerStats[1], 2)
        else:
            archerKda = "0.00"
        if builderStats[0] != 0:
            builderKda = round(builderStats[0]/builderStats[1], 2)
        else:
            builderKda = "0.00"
        if knightStats[0] != 0:
            knightKda = round(knightStats[0]/knightStats[1], 2)
        else:
            knightKda = "0.00"
        if totalStats[0] != 0:
            totalKda = round(totalStats[0]/totalStats[1], 2)
        else:
            totalKda = "0.00"
        embed=discord.Embed(title="View on KAGstats.com", url=playerData[7], description=f"Showing stats for {playerData[3]} {playerData[2]} ({playerData[1]})", color=0xFFD700)
        embed.set_thumbnail(url=playerData[5])
        embed.add_field(name=f"Archer ({archerKda})", value=f'{archerStats[0]:,} kills {archerStats[1]:,} deaths')
        embed.add_field(name=f"Builder ({builderKda})", value=f'{builderStats[0]:,} kills {builderStats[1]:,} deaths')
        embed.add_field(name=f"Knight ({knightKda})", value=f'{knightStats[0]:,} kills {knightStats[1]:,} deaths')
        embed.add_field(name=f"Total ({totalKda})", value=f'{totalStats[0]:,} kills {totalStats[1]:,} deaths')
        embed.set_author(name="kagstats api", icon_url="https://kagstats.com/favicon.ico")


    else:
        embed=discord.Embed(title="kagstats", url="https://kagstats.com", description=f"could not find user {name}", color=0xFFD700)

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'Tracking {apiData[1]:,} kills by {apiData[0]:,} players across {apiData[2]} servers\n{disp_name} using KAGstats {apiData[3]}')
    await interaction.followup.send(embed=embed)


# Loop
@tasks.loop(minutes=5)
async def status_loop():
    if changeStatus:
        activity_list = cfg["games"]
        status_list = [discord.Status.idle, discord.Status.online, discord.Status.dnd]
        random_status = status_list[random.randint(0,len(status_list)-1)]
        random_activity = activity_list[random.randint(0,len(activity_list)-1)]
        activity = discord.Game(name=random_activity, type=random.randint(1,3))
        await client.change_presence(status=random_status, activity=activity)
        print(f"Status has changed to {random_activity} with icon {random_status}")
    else:
        activity = discord.Game(name="in the snow", type=1)
        await client.change_presence(status=discord.Status.online, activity=activity)
        print("Random change off")


# Legacy
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    '''if message.content.startswith(f'{prefix}gameid'):
        
        

        
        await message.channel.send(f'{steam.detailOutput(gameid)}')'''

    if message.content.startswith(f'{prefix}gameid'):

        print(f'User: {message.author} ran {message.content} in server: {message.guild.name}(id:{message.guild.id}) and channel: {message.channel.mention}')

        input = message.content.replace(f'"', "")
        input = message.content.replace(f'{prefix}gameid ', "")
        await message.channel.send('B')
        embed = steam.embedOutput(input)
        disp_name = str(client.user)[:-5] + " bot"
        embed.set_footer(text=f'{disp_name}')
        await message.channel.send(embed=embed)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith(f'{prefix}a'):
        print(f'User: {message.author} ran {message.content} in server: {message.guild.name}(id:{message.guild.id}) and channel: {message.channel.mention}')
        activity = discord.Game(name="with Steam API", type=3)
        await client.change_presence(status=discord.Status.idle, activity=activity)



token = cfg["token"]
client.run(token)