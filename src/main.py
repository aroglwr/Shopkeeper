import discord
from discord import app_commands
from discord import FFmpegPCMAudio
from discord.ext import tasks
import API.general as general
import API.steam as steam
import API.league as league
import API.kag as kag
import API.nasa as nasa
import API.reddit as reddit
import API.chesscom as chess
import API.mal as mal
import time, datetime
#import API.hypixel as hp
import random
from asyncio import run
from typing import Literal


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


prefix = "!"
changeStatus = True # random status change
cfg = general.getJSON_local_old("src/config.json")
data = general.getJSON_local_old("src/data.json")

# config file stuff
bot_version = cfg["version"]
steam_token = cfg["steam_token"]
riot_token = cfg["riot_token"]
nasa_token = cfg["nasa_token"]
mal_client = cfg["mal_client"]

# data file stuff
summonerEmoji = data["riot"]["leagueSummonerSpells"]
runeEmoji = data["riot"]["leagueRunes"]
startTime = time.time()
faqs = data["faq"]

activity_list = data["games"]
watch_list = data["watching"]


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
    cache_loop.start()
    print(f'We have logged in as {client.user}')
# Generic Commands
@tree.command(name = "gif", description = "Funny gif generator")
async def gif(interaction: discord.Interaction):
    await interaction.response.defer()
    gifList = data["gifs"]
    gifOut = gifList[random.randint(0,len(gifList)-1)] 
    await interaction.followup.send(gifOut)
    #await interaction.response.send_message(gifOut)
@tree.command(name = "crunch", description = "Crunch!")
async def crunch(interaction: discord.Interaction):
    
    await interaction.response.defer()
    gifList = data["crunch"]
    gifOut = gifList[random.randint(0,len(gifList)-1)]
    await interaction.followup.send(gifOut)



@tree.command(name = "about", description = f"About {str(client.user)[:-5]}")
async def about(interaction: discord.Interaction):
    """about description
    """
    await interaction.response.defer(ephemeral=False)
    uptime = str(datetime.timedelta(seconds=int(time.time()-startTime)))
    pythonVer, discordVer, kagVer = [await general.getVersion(), f"{discord.version_info[0]}.{discord.version_info[1]}.{discord.version_info[2]}", (await kag.getWebStatus())[3]]
    
    # stats
    guilds = client.guilds
    memberCount = 0
    for guild in guilds:
        for member in guild.members:
            if not member.bot:
                memberCount += 1

    serverCount, userCount = [str(len(guilds)), memberCount]
    embed=discord.Embed(title=f'View on GitHub', url=f'https://github.com/aroglwr', description='If you notice any issues\nplease contact [aroglwr](https://twitter.com/aroglwr)', color=0x0000ff)
    embed.add_field(name=f"Servers", value=f"{serverCount} servers")
    embed.add_field(name=f"Users", value=f"{userCount} users")
    embed.add_field(name=f"Uptime", value=f"{uptime}")

    embed.add_field(name="Python", value=f"[{pythonVer}](https://www.python.org/)")
    embed.add_field(name="discord.py", value=f"[{discordVer}](https://discordpy.readthedocs.io/en/stable/)")
    embed.add_field(name="KAGstats", value=f"[{kagVer}](https://kagstats.com)")
    #embed.add_field(name = "test", value = "```\ntest \n test1```", inline=False)


    embed.set_author(name=f'{client.user.display_name} {bot_version}', icon_url=client.user.display_avatar.url)
    #embed.set_thumbnail(url=client.user.display_avatar.url)

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')

    await interaction.followup.send(embed=embed)

@tree.command(name = "faq", description = f"Frequently Asked Questions")
async def faq(interaction: discord.Interaction):
    """faq description
    """
    
    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(title="Frequently Asked Questions", description="Here are a list of frequently asked questions", color=0x0000ff)
    for question, answer in faqs.items():
        embed.add_field(name=question, value=answer, inline=False)


    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')

    await interaction.followup.send(embed=embed)

@tree.context_menu(name="Profile information!")
async def getProfile(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer(ephemeral=True)

    member = user.guild.get_member(user.id)

    embed = discord.Embed(title=f"Showing data for {user.name}{f' (bot)' if user.bot else ''}", description=f"", color=0x0000ff)
    embed.set_thumbnail(url=user.avatar)
    
    embed.add_field(name="Roles", value=", ".join([role.mention for role in user.roles]), inline=False)
    
    embed.add_field(name="Join Date", value=f"<t:{int(user.created_at.timestamp())}>", inline=False)
    activities = member.activities
    if activities is not None:
        for activity in activities:
            if isinstance(activity, discord.activity.Spotify):
                embed.add_field(name="Listening to", value=f"{activity.title} by {activity.artist}")
            if isinstance(activity, discord.activity.Game):
                embed.add_field(name="Activity", value=f"Playing {activity.name}")
            if isinstance(activity, discord.activity.Activity):
                embed.add_field(name="Activity", value=f"{'Playing' if activity.type == discord.ActivityType.playing else ('Watching' if activity.type == discord.ActivityType.watching else 'Streaming')} {activity.name}")

    else:
        activity_text = "None"
        embed.add_field(name="Activity", value=activity_text, inline=False)
    await interaction.followup.send(embed=embed)


'''@tree.command(name = "profilepicture", description = f"Gets profile picture of user")
async def about(interaction: discord.Interaction, user: discord.User):
    """profilepicture description
    Args:
        user (discord.User): User to grab profile picture of
    """
    await interaction.response.defer(ephemeral=False)
    embed = discord.Embed(title=f"Profile picture for {user.name}", description=f"", color=0x0000ff)
    embed.set_image(url=user.avatar)
    await interaction.followup.send(embed=embed)
'''

@tree.command(name = "osu", description = "Command for osu!")
async def osu(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    embed=discord.Embed(title=f'osu! is currently not supported', description=f'There are no plans to add support\nPlease use another bot for all of your [osu!](https://osu.ppy.sh/home) needs', color=0xff66aa)
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Osu%21_Logo_2016.svg/2048px-Osu%21_Logo_2016.png")
    embed.add_field(name="BathBot", value="[Link](https://github.com/MaxOhn/Bathbot)")
    embed.add_field(name="owo!", value="[Link](http://owo-bot.xyz/)")
    embed.add_field(name="AxerBot", value="[Link](https://github.com/AxerBot/axer-bot)")
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'ᵖˡᵃʸ ᵗᵃᶦᵏᵒ\n{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "astrophoto", description = "Shows the Astronomy Photo of The Day from NASA")
async def astrophoto(interaction: discord.Interaction, random: bool=False, hd: bool=False):
    """astrophoto description

    Args:
        random (bool): Show a random image or not
        hd (bool): Show the image in HD or not
    """
    await interaction.response.defer()
    title, desc, date, author, image = await nasa.apod(nasa_token, hd=hd, random=random)
    author = author.replace("\n", "")
    embed=discord.Embed(title=f'{title} ({author}) - {date}', description=desc, color=0x0f52ba)
    embed.set_author(name="Courtesy of NASA", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/NASA_logo.svg/1224px-NASA_logo.png")
    embed.set_image(url=image)

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "wizardposting", description = "Generates a wizardpost from reddit.com/r/wizardposting")
async def wizardposting(interaction: discord.Interaction):
    """wizardposting description
    """
    await interaction.response.defer()
    posts = await reddit.subsearch("wizardposting")
    title, description, author, link, image = posts[random.randint(0, len(posts)-1)]

    embed=discord.Embed(title=f"{title} - {author}", url=f"https://reddit.com{link}", description=description, color=0xff5700)
    embed.set_image(url=image)

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f"{disp_name}")
    await interaction.followup.send(embed=embed)
# Steam Commands
@tree.command(name = "steamgameinfo", description = "Gets game data from Steam website")
async def steamgameinfo(interaction: discord.Interaction, name_or_id: str):
    """steamgameinfo description

    Args:
        name_or_id (str): Game name (punctuation required) or unique URL ID
    """
    await interaction.response.defer()
    # Loading panel
    embed_load=discord.Embed(title=f'', description=f'Please wait', color=0x00afff)
    embed_load.set_author(name=f'Searching Steam Database', icon_url="https://i.gifer.com/ZKZg.gif")
    update = await interaction.followup.send(embed=embed_load)
    
    
    appid = await steam.parseID(name_or_id)
    #p = steam.getPrice(appid)
    try:
        info, images, genres, priceData = await steam.gameData(appid)
        store_page = f'https://store.steampowered.com/app/{appid}/{info[0].replace(" ","_")}'
        coverImage = f'https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/hero_capsule.jpg'
        players_online = (await general.getJSON(f'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key={steam_token}&appid={appid}'))["response"]["player_count"]

        embed=discord.Embed(title=f'Store Page', url=store_page, description=info[1], color=0x1a1aff)
        embed.set_author(name=f'{info[0]} ({appid})', icon_url=f'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/800px-Steam_icon_logo.svg.png')
        embed.set_thumbnail(url=coverImage)
        embed.add_field(name="Developer", value =info[2][0] )
        embed.add_field(name="Publisher", value =info[3][0] )
        embed.add_field(name="Genres", value=general.unpackList(genres, True))
        try:
            if priceData[6] != 0:
                costText = f"~~{priceData[4]}~~ {priceData[3]} {priceData[5]} (-{priceData[6]}%)"
                
            else:
                costText=f"{priceData[3]} {priceData[5]}"
        except:
            costText = "Free"
        embed.add_field(name="Cost", value =costText)
        embed.add_field(name="Players Online", value =f"{players_online:,}" )
        embed.add_field(name="Released", value = f"{info[4]['date']}")
    
    except:
        embed=discord.Embed(title=f'', description=f'', color=0x0080ff)
        embed.set_author(name=f'Could not find game', icon_url=f'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/800px-Steam_icon_logo.svg.png')



    """
    try:
        
        image = f'https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/hero_capsule.jpg'
        gameName = steam.getName(appid)
        gameNameURL = gameName.replace(" ","_")
        store_page = f'https://store.steampowered.com/app/{appid}/{gameNameURL}'
        embed=discord.Embed(title=f'Store Page', url=store_page, description="dummy", color=0x1a1aff)

        embed.set_author(name=f'{gameName} ({appid})', icon_url=f'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/800px-Steam_icon_logo.svg.png')
        embed.set_thumbnail(url=image)

        description_text = f'Is {p[3]} {p[4]}'
        if p[5] != 0:
            description_text += f' and is {p[5]}% on sale!'
        else:
            pass
        
        if p[5] != 0:
            embed.add_field(name="Price Before", value=p[6])
            embed.add_field(name="Price After", value=p[3])
        else:
            embed.add_field(name=f'This is so sad', value=":sob: literally me")

        players_online = steam.getJSON(f'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key={steam_token}&appid={appid}')["response"]["player_count"]
        embed.add_field(name=f'Players Online', value=f'{players_online:,}')
    except:
        embed=discord.Embed(title=f'', description=f'', color=0x0080ff)
        embed.set_author(name=f'Could not find game', icon_url=f'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/800px-Steam_icon_logo.svg.png')
    
    """
    
    
    disp_name = str(client.user)[:-5] + " bot"

    embed.set_footer(text=f'{disp_name}')
    update= await update.edit(embed=embed)
    #await interaction.followup.send(embed=embed)

@tree.command(name = "steamuser", description = "Gets user data from Steam website")
async def steamuser(interaction: discord.Interaction, name: str):
    """steamuser description

    Args:
        name (str): Vanity URL or profile ID
    """
    await interaction.response.defer()
    
    try:
        isPrivate, username, creationDate, rounded_ptime, profilePicture, profileRegion, gamesCount, (player_status, inGame), profileURL, profilePicture_small, lastLogoff = await steam.accountInfo(steam_token, name)
        bans = await steam.accountBans(steam_token, name)
        if isPrivate == 3:
            flag = ""
            if profileRegion != "":
                profileRegion= f'({profileRegion})'
                flag = f":flag_{profileRegion[1:-1].lower()}: "
                
            if inGame != "":
                online_status = f"is playing {inGame}"
            elif player_status == 1:
                online_status = "is online"
            else:
                online_status = f"was last online <t:{lastLogoff}:R>"


            embed=discord.Embed(title=f'Profile Link', url=profileURL, description=f'{flag}{username} {online_status}', color=0x0080ff)
            embed.set_author(name=f'{username} {profileRegion}', icon_url=f'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/800px-Steam_icon_logo.svg.png')
            embed.add_field(name="Account Created", value=creationDate)
            embed.add_field(name="Game Library", value=f'{gamesCount:,} games')
            embed.add_field(name="Total Playtime", value=f'{rounded_ptime:,} hours')
            embed.add_field(name="VAC Bans?", value=f'{bans[2]}')
            embed.add_field(name="Community Ban?", value=f'{bans[0]}')
            embed.add_field(name="Trade Ban?", value=f'{bans[1]}')
            embed.set_thumbnail(url=profilePicture)
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
    """steamachievementinfo description

    Args:
        username (str): Vanity URL or profile ID
        name_or_id (str): Game name (punctuation required) or unique URL ID
    """
    await interaction.response.defer()
    appid = await steam.parseID(name_or_id)
    try:
        image = f'https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/hero_capsule.jpg'
        gameName = await steam.getName(appid)
        store_page = f'https://store.steampowered.com/app/{appid}/{gameName.replace(" ","_")}'
        achievement_info = await steam.achievementInfo(steam_token, username, name_or_id)
        info = await steam.accountInfo(steam_token, username)
        embed=discord.Embed(title=f"Stats for {gameName}", url=store_page, description=f'{info[1]} has {achievement_info[1]}/{achievement_info[3]} ({achievement_info[2]}%) achievements for {gameName}', color=0x0000ff)
        embed.set_author(name=f'{info[1]} ({info[5]})', icon_url=f'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/800px-Steam_icon_logo.svg.png')
        embed.set_thumbnail(url=image)
    except:
        embed=discord.Embed(title=f"", url="", description=f'', color=0x0000ff)
        embed.set_author(name=f'Could not load achievements for user', icon_url=f'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/800px-Steam_icon_logo.svg.png')
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    
    #messageOut = f'Steam user {steam.accountInfo(steam_token, userid_input)[0]} for game {appid_name}\nHas {achievement_info[2]}% completion.'
    #print(messageOut)
    await interaction.followup.send(embed=embed)

# League Commands
@tree.command(name = "masterysearch", description = "Search a League of Legends summoner's mastery data by champion")
async def masterysearch(interaction: discord.Interaction, region: str, game_name: str, champion: str, tagline: str=None):
    """masterysearch description

    Args:
        region(str): Where that summoner is registered in e.g. euw, na, kr
        game_name (str): Name of account
        tagline (str): Account tagline e.g. #EUW
        
        champion (str): Name of champion
    """
    await interaction.response.defer()
    try:
        summoner_data = await league.getSummonerData(game_name, tagline, region, riot_token)
        print(f'https://championmastery.gg/summoner?summoner={summoner_data[6]}%23{summoner_data[8]}' + f'&region={region.upper()}&lang=en_US')
        summonerExists=True
        masterySearch = await league.masterySearch(summoner_data[1], champion, riot_token, region)
        
        if summonerExists:
            if masterySearch[2] >= 4:
                image = f'https://raw.communitydragon.org/latest/game/assets/ux/mastery/legendarychampionmastery/masterycrest_level_{masterySearch[2]}_art.png'
            else:
                image = "https://raw.communitydragon.org/latest/game/assets/ux/mastery/legendarychampionmastery/masterycrest_level_0_art_mini.png"
            embed=discord.Embed(title=f'ChampionMastery.GG', url=f'https://championmastery.gg/player?riotId={summoner_data[6]}%23{summoner_data[8]}&region={region.upper()}&lang=en_US', description=f'{await league.getChampionName(masterySearch[1])} with {masterySearch[0]:,} points at level {masterySearch[2]}', color=0x0000ff)
            embed.add_field(name="Last Played", value=f"<t:{str(masterySearch[3])[:-3]}:d>")
            embed.add_field(name="Progress", value=f"{masterySearch[0]}/{masterySearch[0] + masterySearch[4]}")
            embed.set_author(name=f'{summoner_data[7]}#{summoner_data[8]} ({region.upper()})', icon_url=image)
            embed.set_thumbnail(url=f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{masterySearch[1]}.png')
    except:
        try:
            if summonerExists:
                embed=discord.Embed(title=f"Data could not be found for {summoner_data[0]} ({region.upper()}) on {champion}")
        except:
            embed=discord.Embed(title=f"Could not find summoner {game_name} {'(' + region.upper() + ')' if tagline is None else '#' + tagline.upper()}", description='', color=0x0000ff)
        embed.set_thumbnail(url="https://static.wikia.nocookie.net/leagueoflegends/images/c/c0/LoL_ping_missing.png")
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

''' i dont like this command - all info can be found using masteryprofile + masterysearch anyway
@tree.command(name = "highestmastery", description = "Displays user's highest League of Legends champion mastery")
async def highestmastery(interaction: discord.Interaction, summoner_name: str, region: str):
    """highestmastery description

    Args:
        summoner_name (str): Name of summoner
        region(str): Where that summoner is registered in e.g. euw, na, kr
    """
    await interaction.response.defer()

    summoner_data = await league.getSummonerData(summoner_name, region, riot_token)
    highestMastery = await league.highestMasteryData(summoner_data[5], riot_token, region)
    if highestMastery[4] >= 4:
        image = f'https://raw.communitydragon.org/latest/game/assets/ux/mastery/mastery_icon_{highestMastery[4]}.png'
    else:
        image = "https://raw.communitydragon.org/latest/game/assets/ux/mastery/mastery_icon_default.png"

    embed=discord.Embed(title=f'View on ChampionMastery.GG', url=f'https://championmastery.gg/summoner?summoner={summoner_data[6]}&region={region.upper()}&lang=en_US', description=f'{summoner_data[0]} has highest mastery on {await league.getChampionName(highestMastery[3])} with {highestMastery[0]:,} (level {highestMastery[4]})', color=0x0000ff)
    embed.add_field(name=f"Chest Earned?", value=f"{highestMastery[1]}")
    embed.add_field(name="Progress", value=f'{highestMastery[2]}')
    embed.set_author(name=f'{summoner_data[0]} ({region.upper()})', icon_url=image)
    embed.set_thumbnail(url=f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{highestMastery[3]}.png")

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)'''

@tree.command(name = "match_history", description = "Displays user's League of Legends match history")
async def matchhistory(interaction: discord.Interaction, region: str, game_name: str, tagline: str=None):
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
    try:
        summonerData =  await league.getSummonerData(game_name, tagline, region, riot_token)
        matchData = await league.getMatchHistory(riot_token, summonerData[1], region, 5)
        rankedData = await league.getRankedData(riot_token, summonerData[5], region)
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
                embed=discord.Embed(title=f'View on OP.GG', url=f'https://www.op.gg/summoners/{region}/{summonerData[6]}', description=f'{summonerData[0]} has {winRate:.2f}% WR in {rankedQueue} and is {rankedTier.capitalize()} {rank} {leaguePoints} LP', color=0x0000ff)
                embed.add_field(name="Progress to Promotion", value=f"`{general.progressBar(20, leaguePoints/100)}` {promoStatus}", inline=False)
                embed.set_author(name=f'{summonerData[0]} ({region.upper()}) - {rankedWins}W/{rankedLosses}L', icon_url=rankIcon)
            else:
                rankIcon = rankedData [1]
                embed=discord.Embed(title=f'View on OP.GG', url=f'https://www.op.gg/summoners/{region}/{summonerData[6]}', description=f'No ranked data for {summonerData[0]}', color=0x0000ff)
                embed.set_author(name=f'{summonerData[0]} ({region.upper()})', icon_url=rankIcon)
            champName, win, role, gameType = matchData[1]
            
            
            embed.set_thumbnail(url=(await league.getSummonerIcon(summonerData[3])))

            for i in range(len(win)):
                embed.add_field(name="W/L", value=f'{win[i]}')
                embed.add_field(name="Gamemode", value=f'{gameType[i]}')
                if role[i] != "Invalid":
                    embed.add_field(name="Champion", value=f'{champName[i]} {role[i]}')
                else:
                    embed.add_field(name="Champion", value=f'{champName[i]}')
        #else:
        #    embed=discord.Embed(title="Could not load match history", description='', color=0x0000ff)
        #    embed.set_thumbnail(url="https://static.wikia.nocookie.net/leagueoflegends/images/c/c0/LoL_ping_missing.png")
    except:
            embed=discord.Embed(title="Could not load match history", description='', color=0x0000ff)
            embed.set_thumbnail(url="https://static.wikia.nocookie.net/leagueoflegends/images/c/c0/LoL_ping_missing.png")

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')

    # Send the embed update
    update= await update.edit(embed=embed)

@tree.command(name = "championdata", description="Gets data for a League of Legends champion")
async def championdata(interaction: discord.Interaction, champion_name: str):
    """championdata description

    Args:
        champion_name (str): Name of champion
    """
    await interaction.response.defer()
    try:
        championData = await league.getChampionData(champion_name)

        embed=discord.Embed(title=f'{championData[0]} {championData[1]}', description=f'{championData[2]}', color=0xff7518)
        embed.add_field(name=f"Skins: {len(championData[9][1:])}", value=f"[Click to view online](https://teemo.gg/viewer/league-of-legends/champions/{championData[10]}/0)", inline=False)
        #embed.add_field(name="Spells", value="", inline=False)
        embed.add_field(name="Tags", value=f'{championData[5]}')
        embed.add_field(name="Resource Bar", value=f'{championData[7]}')
        #embed.set_image(url=championData[3])
        if championData[8] != None:
            embed.add_field(name="Tip", value=f'{str(championData[8])}', inline=False)
        embed.set_thumbnail(url=championData[3])
    except:
        embed=discord.Embed(title=f"Could Not Find Champion \"{champion_name}\"", color=0xff7518)
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "itemdata", description="Gets data for a League of Legends item")
async def itemdata(interaction: discord.Interaction, item_name: str):
    """itemdata description

    Args:
        item_name (str): Name of item
    """
    
    rep = {
        "<mainText>": "",
        "</mainText>": "",
        "<stats>": "",
        "</stats>": "",
        "<attention>": "",
        "</attention>": "",
        "<br>": "\n",
        "<passive>": "**",
        "</passive>": "**",
        "<scaleAP>": "",
        "</scaleAP>": "",
        "<ornnBonus>": "**",
        "</ornnBonus>": "**",
        "<attackSpeed>": "",
        "</attackSpeed>": "",
        "<li>": "\n",
        "<healing>": "",
        "</healing>": "",
        "<goldGain>": "",
        "</goldGain>": "",
        "<OnHit>": "",
        "</OnHit>": "",
        "<rarityMythic>": "",
        "</rarityMythic>": "",
        "<rarityLegendary>": "",
        "</rarityLegendary>": ""
    }
    
    await interaction.response.defer()
    try:
        itemIcon, itemCost, itemDesc, itemName_f, build_path, builds_into, itemCombine, itemSell, ornn, itemDetail = await league.getItemData(item_name)

        # desc filtering
        for item in rep:
            itemDetail = itemDetail.replace(item, rep[item])
        itemDetail = itemDetail.split("<active>", 1)[0]

        # ornn check! :)
        if ornn:
            itemName_f = f'{itemName_f} <:ornn_circle:1207422369325514833>'

        if itemDesc == "":
            embed=discord.Embed(title=f'Data for {itemName_f}', description=itemDetail, color=0xff7518)
        else:
            embed=discord.Embed(title=f'Data for {itemName_f}', description=f'{itemDesc}.\n{itemDetail}', color=0xff7518)
        embed.add_field(name="Cost", value=f"{itemCost} <:gold:1148709055087521883>")
        embed.add_field(name="Combine Cost", value=f"{itemCombine} <:gold:1148709055087521883>")
        embed.add_field(name="Sell Value", value=f"{itemSell} <:gold:1148709055087521883> ({int(itemSell*100/itemCost)}%)")
        print(general.unpackList(build_path, True))
        print(general.unpackList(builds_into, True))
        if build_path != []:
            embed.add_field(name="Build Path", value=general.unpackList(build_path, True))
        if builds_into != []:
            embed.add_field(name="Builds Into", value=general.unpackList(builds_into, True))
        #embed.set_image(url=championData[3])
        embed.set_thumbnail(url=itemIcon)
    except:
        embed=discord.Embed(title=f"Could Not Find Item \"{item_name}\"", color=0xff7518)
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "weeklyrotation", description = "Gets League of Legends champions which are on the weekly rotation")
async def weeklyrotation(interaction: discord.Interaction):
    await interaction.response.defer()

    
    embed=discord.Embed(title="This Week's Champions Are:", description=f'{general.unpackList(await league.getWeeklyRotation(riot_token), True)}', color=0xff7518)

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "leaguelivegame", description = "Gets live game data for a League of Legends player")
async def leaguelivegame(interaction: discord.Interaction, region: str, game_name: str, tagline: str=None):
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


    summoner_data = await league.getSummonerData(game_name, tagline, region, riot_token)
    liveGameData = await league.getLiveGame(riot_token, summoner_data[5], region, summonerEmoji, runeEmoji)    
    if liveGameData[0] == True:
        embed=discord.Embed(title=f'View on OP.GG (Spectate)', url=f'https://www.op.gg/summoners/{region}/{summoner_data[6]}/ingame', description=f'{summoner_data[0]} is playing {liveGameData[3]} in {liveGameData[2][1]} on {liveGameData[2][0]}\nGame started <t:{liveGameData[7]}:R>', color=0x0000ff) # Summoner has been in game for {liveGameData[7][0]} minutes {liveGameData[7][1]} seconds
        #primaryTree = liveGameData[8][1][:4]
        #secondaryTree = general.unpackList(liveGameData[8][1][4:6])
        runeEmojis = liveGameData[8]
        embed.add_field(name="Spells", value=f'{liveGameData[6][0]} {liveGameData[6][1]}')
        embed.add_field(name="Runes", value=f'{runeEmojis[0]} {runeEmojis[1]} {runeEmojis[2]}{runeEmojis[3]}\n{runeEmojis[4]} {runeEmojis[5]}')
        print(general.unpackList(list(liveGameData[4][0] + liveGameData[4][1]), True))
        print(list(liveGameData[4][0] + liveGameData[4][1]))
        
        embed.add_field(name="Banned Champions", value=f'{general.unpackList((liveGameData[4][0] + liveGameData[4][1]), True)}', inline=False)
        embed.add_field(name="", value=f'')
        embed.add_field(name="", value=f'')
        embed.set_author(name=f'{summoner_data[0]}#{summoner_data[8]} ({region.upper()})', icon_url=(await league.getSummonerIcon(summoner_data[3])))
        embed.set_thumbnail(url=liveGameData[5])
    else:
        embed=discord.Embed(title="Summoner is not in game", description='', color=0x0000ff)
        embed.set_thumbnail(url="https://static.wikia.nocookie.net/leagueoflegends/images/c/c0/LoL_ping_missing.png")
    #except:
    #    embed=discord.Embed(title="Could not find summoner", color=0x0000ff)
    #    embed.set_thumbnail(url="https://static.wikia.nocookie.net/leagueoflegends/images/c/c0/LoL_ping_missing.png")

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    #await interaction.followup.send(embed=embed)
    # Send the embed update
    update= await update.edit(embed=embed)
    

@tree.command(name = "gameanalysis", description= "Gets an analysis of a single League of Legends game")
async def gameanalysis(interaction: discord.Interaction, region: str, game_name: str, tagline: str=None, game_number: int = 1):
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


    summonerData =  await league.getSummonerData(game_name, tagline, region, riot_token)
    match_history = await league.getMatchHistory(riot_token, summonerData[1], region, game_number)
    print(match_history)
    match_id= match_history[2][0][game_number-1]
    
    region_f = match_history[2][1]
    mapType = match_history[1][3][game_number-1]
    

    kills = await league.drawMap(riot_token, match_id, region_f, mapType, summonerData[1]) # https://europe.api.riotgames.com/lol/match/v5/matches/EUW1_6579462123/timeline?api_key=RGAPI-b560a406-267a-4dfe-b7a8-c14b5c6f2a50
    file = discord.File(f"src/files/LeagueMaps/{match_id[:2]}/{match_id}.png", filename="map.png")



    embed = discord.Embed(title="game analysis", description=f"Score: {kills[0]} B vs R {kills[1]}")

    embed.set_image(url="attachment://map.png")



    
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    #await interaction.followup.send(embed=embed)
    # Send the embed update
    await interaction.followup.send(file=file, embed=embed)

@tree.command(name = "masteryprofile", description = "Gets mastery info for a League of Legends accounts")
async def masteryprofile(interaction: discord.Interaction, region: str, game_name: str, tagline: str=None):
    """masteryprofile description

    Args:
        summoner_name (str): Name of summoner
        region(str): Where that summoner is registered in e.g. euw, na, kr
    """
    await interaction.response.defer()

    mastery_icons = ["<:Mastery_5:1151232094245245010>","<:Mastery_6:1151232090034147328>","<:Mastery_7:1151232092500398220>"]
    
    summonerData = await league.getSummonerData(game_name, tagline, region, riot_token)



    tagline = region if not tagline else tagline
    icon = await league.getSummonerIcon(summonerData[3])#
    masteryData = await league.masteryGraph(riot_token, summonerData[1], region)

    level_list = masteryData[3]
    highest = masteryData[0]
    embed = discord.Embed(title="Mastery Profile", description=f"Showing data for {summonerData[7]}#{summonerData[8]}", color=0x0000ff)
    
    embed.add_field(name="Highest", value=f"{list(highest.keys())[0]} - {list(highest.values())[0]:,}\n{list(highest.keys())[1]} - {list(highest.values())[1]:,}\n{list(highest.keys())[2]} - {list(highest.values())[2]:,}")
    embed.add_field(name="Statistics", value=f"{sum(j >= 10 for j in masteryData[3])}x <:Mastery_10:1246451010583662623> (level 10+) \nTotal Points: {masteryData[1]:,}\nAverage Points - {int(masteryData[1]/masteryData[2]):,}")
    embed.set_thumbnail(url=icon)
    embed.set_image(url=f"attachment://{game_name.lower().replace(' ', '')}{tagline.lower()}.png")
    file = discord.File(f"src\\files\\SummonerMastery\\{summonerData[1]}.png", filename=f"{game_name.lower().replace(' ', '')}{tagline.lower()}.png")

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f"{disp_name}")

    await interaction.followup.send(file=file, embed=embed)

@tree.command(name = "runedata", description = "Gets rune data")
async def runedata(interaction: discord.Interaction, search: str):
    """runedata description

    Args:
        search (str): Name of rune to search
    """
    await interaction.response.defer()

    found, name, description, rune_icon, id_, perk_tree, perk_tree_icon = await league.searchRune(search)

    rune_colour = {
        "Domination":0xe00844,
        "Resolve":0x3bb143,
        "Inspiration":0x2d87a0,
        "Sorcery":0xd552f9,
        "Precision":0xfeab36
    }


    if found:
        embed = discord.Embed(title=f"Data for {name}", description=description, color=rune_colour[perk_tree])
        embed.set_author(name=perk_tree, icon_url=perk_tree_icon)
        embed.set_thumbnail(url=rune_icon)  
    else:
        ""
        
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f"{disp_name}")

    await interaction.followup.send(embed=embed)
# KAG Commands
@tree.command(name = "kagstats", description="Gets King Arthur's Gold Stats for a player")
async def kagstats(interaction: discord.Interaction, name: str):
    """kagstats description

    Args:
        name (str): Name of user to search for
    """
    await interaction.response.defer()

    apiData = await kag.getWebStatus()
    playerData = await kag.getPlayerData(await kag.searchPlayer(name))

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
        embed.add_field(name="Account Created", value=playerData[8])
        #embed.set_author(name="kagstats api", icon_url="https://kagstats.com/favicon.ico")


    else:
        embed=discord.Embed(title="KAGstats.com", url="https://kagstats.com", description=f"Could not find user {name}", color=0xFFD700)

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'Tracking {apiData[1]:,} kills by {apiData[0]:,} players across {apiData[2]} servers\n{disp_name} powered by KAGstats {apiData[3]}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "kagservers", description="Gets King Arthur's Gold Server list")
async def kagservers(interaction: discord.Interaction, official_only: bool = False):
    """kagservers description

    Args:
        official_only (bool): Filter only official servers
    """
    
    await interaction.response.defer()

    # Loading panel
    embed_load=discord.Embed(title=f'', description=f'Please wait', color=0xFFD700)
    embed_load.set_author(name=f'Searching Available Servers', icon_url="https://i.gifer.com/ZKZg.gif")
    update = await interaction.followup.send(embed=embed_load)


    apiData = await kag.getWebStatus()
    servers = await kag.getServerList(official_only)

    serverList = servers[0][:5]
    try:
        if official_only:
            desc_text = f"There are currently {servers[1]} players on [official](https://kagstats.com/#/servers) TDM, TTH, CTF and Small CTF servers"
        else:
            desc_text = f"There are currently {servers[1]} players online"
        embed=discord.Embed(title="King Arthur's Gold Server List", description=f"{desc_text}\nLast updated <t:{int(time.time())}:R>", color=0xFFD700) # f"Last updated {general.dateConvert(time.time())[1][:-1]}"
        embed.set_thumbnail(url="")
        for server in serverList:
            #embed.add_field(name=server[2][0], value=server[2][0])
            #embed.add_field(name="Player Count", value=server[0])
            #embed.add_field(name="Server Address", value=f'{server[1][0]}:{server[1][1]}')
            link = f"kag://{server[1][0]}:{server[1][1]}"
            playerList = server[3]
            playerList.sort()
            embed.add_field(name=server[2][0], value=f'**Address:** {link}\n**Gamemode**: {server[2][2]}\n**Players:** {server[0][0]}/{server[0][1]}\n{general.unpackList(playerList, True)}', inline=False)
            embed.add_field(name="", value="")
    except:
        embed=discord.Embed(title="King Arthur's Gold Server List", description=f"Could not find any servers\nLast updated <t:{int(time.time())}:R>", color=0xFFD700)

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'Tracking {apiData[1]:,} kills by {apiData[0]:,} players across {apiData[2]} servers\n{disp_name} powered by KAGstats {apiData[3]}')

    # Send the embed update
    update= await update.edit(embed=embed)
    #await interaction.followup.send(embed=embed)

@tree.command(name = "kagclans", description="Gets King Arthur's Gold Clan Information")
async def kagclans(interaction: discord.Interaction, search: str = ""):
    """kagclans description

    Args:
        search (str): Name of clan to search (leave blank for a list of top clans)
    """
    await interaction.response.defer()

    # Loading panel
    embed_load=discord.Embed(title=f'', description=f'Please wait', color=0xFFD700)
    embed_load.set_author(name=f'Searching Clans', icon_url="https://i.gifer.com/ZKZg.gif")
    update = await interaction.followup.send(embed=embed_load)

    apiData = await kag.getWebStatus()
    

    if search:
        clan = await kag.searchClan(search)
        if clan[0]:
            clanInfo = clan[1]
            members = await kag.getClanMembers(clanInfo[7])
            embed=discord.Embed(title="View on KAGstats.com", url=f"https://kagstats.com/#/clans/{clanInfo[7]}", description=f"Showing stats for {clanInfo[0]}", color=0xFFD700)
            embed.set_thumbnail(url=(await kag.getPlayerData(clanInfo[2]))[5])
            embed.add_field(name=f"Created", value=f"<t:{clanInfo[1]}:D>")
            embed.add_field(name=f"Leader", value=f"{clanInfo[5]} ({clanInfo[4]})")
            embed.add_field(name=f"Total Members", value=f"{clanInfo[3]}")
            embed.add_field(name="Members", value=general.unpackList(members, True))
        else:
            embed=discord.Embed(title="KAGstats.com", url=f"https://kagstats.com/#/clans", description=f'Could not find clan {search}', color=0xFFD700)
    else:
        
        clans = await kag.getClanList()
        embed=discord.Embed(title="View on KAGstats.com", url="https://kagstats.com/#/clans", description=f"Found {len(clans)} clans total", color=0xFFD700)
        for clan in clans[:5]: 
            #embed.add_field(name=clan[0], value=f"**Created on:** <t:{clan[1]}:D>\n**Owner:** {clan[4][1]} ({clan[4][0]})\n**Members:** {clan[3]}", inline=False)
            embed.add_field(name=f"Name", value=f"{clan[0]} <t:{clan[1]}:D>")
            embed.add_field(name=f"Leader", value=f"{clan[4][1]}")
            embed.add_field(name=f"Members", value=f"{clan[3]}")
            
        #embed.set_thumbnail(url="https://kagstats.com/favicon.ico")

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'Tracking {apiData[1]:,} kills by {apiData[0]:,} players across {apiData[2]} servers\n{disp_name} powered by KAGstats {apiData[3]}')
    # Send the embed update
    update= await update.edit(embed=embed)



@tree.command(name = "kagleaderboard", description="Gets King Arthur's Gold Clan Information")
async def kagleaderboard(interaction: discord.Interaction, filter: Literal["Knight", "Builder", "Archer"]="Global",monthly: bool = False):

    await interaction.response.defer()
    
    # Loading panel
    embed_load=discord.Embed(title=f'', description=f'Please wait', color=0xFFD700)
    embed_load.set_author(name=f'Searching Leaderboard', icon_url="https://i.gifer.com/ZKZg.gif")
    update = await interaction.followup.send(embed=embed_load)

    if monthly and filter == "Global":
        embed= discord.Embed(title="Total monthly leaderboard is not supported", value="Please try a specified class or non-monthly", color=0xFFD700)
    else:


        apiData = await kag.getWebStatus()
        lb_data = await kag.getLeaderboard(classIn=filter, monthly=monthly)
        lb_players = lb_data[0]
        embed = discord.Embed(title="Leaderboard", description="description", color=0xFFD700)
        for i, player in enumerate(lb_players[:5]):
            embed.add_field(name=f"#{i+1}", value=f"{player[0]} {player[1]}")
            embed.add_field(name=f"Kills/Deaths", value=f"{player[3]}/{player[4]}")
            embed.add_field(name=f"KDR", value=f"{(player[3]/player[4]):2.f if player[4] != 0 else player[3]}")
        
    
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'Tracking {apiData[1]:,} kills by {apiData[0]:,} players across {apiData[2]} servers\n{disp_name} powered by KAGstats {apiData[3]}')
    # Send the embed update
    update= await update.edit(embed=embed)

@tree.command(name = "chessprofile", description="Gets Chess.com information")
async def chessprofile(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    try:
        avatar, url, displayname, country, last_online, joined, status, is_streamer, verified, league, title, stream_url = await chess.getUser(username)
        streamerDesc = ""
        if is_streamer:
            streamerDesc = f" \n[View livestream]({stream_url})"

        embed = discord.Embed(title=f"View profile for {title}{displayname} ({country[-2:]})", description=f"Last online <t:{last_online}:R> joined <t:{joined}:D>{streamerDesc}", url=url, color=0x4a3c27)
        
        stats = await chess.getStats(username)
        embed.set_thumbnail(url=avatar)
        for stat in stats:
            embed.add_field(name=stat[0][6:].capitalize(), value=f"Rating: {stat[1][0]}\nW/L/D: {stat[1][1]}/{stat[1][2]}/{stat[1][3]}")
    except:
        embed = discord.Embed(title="User not found", description=f'Could not find user with name "{username}"', color=0x4a3c27)
    embed.set_author(url="https://images.chesscomfiles.com/uploads/v1/images_users/tiny_mce/PedroPinhata/phpkXK09k.png", name="Via Chess.com")
    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)


'''@tree.command(name = "myanimelist", description="Gets MAL user info")
async def myanimelist(interaction: discord.Interaction, username: str):
    await interaction.response.defer()

    statuses = ["watching",  "on_hold", "dropped", "plan_to_watch", "completed"]
    anime_list, count = await mal.user_list(username, mal_client)

    desc_text = ""
    for status in statuses:
        amount = count.get(status)
        status = status.replace('_', ' ')
        status = status.capitalize()
        desc_text += f"{status}: {amount}\n"
    embed = discord.Embed(title=f"Anime for {username}", description=desc_text, url="https://google.com", color=0x4a3c27)
    
    for anime in anime_list:
        embed.add_field(name=f"{anime[0]}", value=f"a", inline=False)


    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)
'''

@tree.command(name = "anime_search", description="Gets anime info from MAL")
async def anime_search(interaction: discord.Interaction, name: str):
    await interaction.response.defer()

    id = await mal.anime_search(name, mal_client)
    name, description, episode_count, studios, genres, runtime, users, name_en, name_jp, url, img = await mal.anime_details(id, mal_client)

    embed = discord.Embed(title=f"{name} ({name_en}/{name_jp})", description=description, url=url, color=0x2e51a2)
    embed.set_thumbnail(url=img)
    
    embed.add_field(name="Genres", value=general.unpackList(genres, True))
    embed.add_field(name="Studio",value=general.unpackList(studios, True))
    embed.add_field(name="Total Episodes", value=episode_count)

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

# Loop
@tasks.loop(minutes=5)
async def status_loop():
    if changeStatus:
        status_list = [discord.Status.online] #[discord.Status.idle, discord.Status.online, discord.Status.dnd]
        random_status = status_list[random.randint(0,len(status_list)-1)]
        if random.randint(0,10) % 2 == 0:
            random_activity = activity_list[random.randint(0,len(activity_list)-1)]
            activity = discord.Game(name=random_activity, type=random.randint(1,3))
            await client.change_presence(status=random_status, activity=activity)
            print(f"Status has changed to {random_activity} with icon {random_status}")
        else:
            random_watch = watch_list[random.randint(0, len(watch_list)-1)]
            activity = discord.Activity(type=discord.ActivityType.watching, name=random_watch)
            await client.change_presence(status=random_status, activity=activity)
            print(f"Status has changed to {random_watch} with icon {random_status}")
    else:
        #activity = discord.Game(name="with the orb", type=1)
        activity = discord.Activity(type=discord.ActivityType.watching, name="the orb")
        await client.change_presence(status=discord.Status.online, activity=activity)
        print("Random change off")


@tasks.loop(minutes=120)
async def cache_loop():
    print("caching")
    await steam.cacheGames()
    await league.cacheLatestPatch()
    print("caching done")

# Legacy
@client.event
async def on_message(message):
    if message.author == client.user:
        return
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
    """if message.content.startswith(f'{prefix}a'):
        print(f'User: {message.author} ran {message.content} in server: {message.guild.name}(id:{message.guild.id}) and channel: {message.channel.mention}')
        activity = discord.Game(name="with Steam API", type=3)
        await client.change_presence(status=discord.Status.idle, activity=activity)"""
    if isinstance(message.channel, discord.DMChannel):
        gifs = data["gifs"]
        emojis = ["😳","🥶","💀","😎","😦"]
        list=[]
        if random.randint(0,1) == 1:
            for gif in gifs:
                list.append(gif)
        else:
            for emoji in emojis:
                list.append(emoji)
        reply_to = await message.channel.fetch_message(message.id)
        await reply_to.reply(list[random.randint(0, len(list)-1)])


token = cfg["token"]
client.run(token)