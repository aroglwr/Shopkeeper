import discord
from discord import app_commands
from discord.ext import tasks
import API.general as general
import API.steam as steam
import API.league as league
import API.kag as kag
import random


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

prefix = "!"
changeStatus = False
cfg = general.getJSON_local("src/config.json")
steam_token = cfg["steam_token"]
riot_token = cfg["riot_token"]
summonerEmoji = cfg["riot"]["leagueSummonerSpells"]


@client.event
async def on_ready():
    await tree.sync()
    # Start the task
    status_loop.start()
    print(f'We have logged in as {client.user}')
@tree.command(name = "gif", description = "Funny gif generator")
async def gif(interaction: discord.Interaction):
    gifList = cfg["gifs"]
    gifOut = gifList[random.randint(0,len(gifList)-1)] 
    await interaction.response.send_message(gifOut)
@tree.command(name = "crunch", description = "Crunch!")
async def crunch(interaction: discord.Interaction):
    gifList = cfg["crunch"]
    gifOut = gifList[random.randint(0,len(gifList)-1)]
    await interaction.response.send_message(gifOut)

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
        embed.add_field(name="Price Before", value=p[5], inline=True)
        embed.add_field(name="Price After", value=p[2], inline=True)
    else:
        embed.add_field(name=f'This is so sad', value=":sob: literally me")

    players_online = steam.getJSON(f'https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?key={steam_token}&appid={appid}')["response"]["player_count"]
    embed.add_field(name=f'Players Online', value=f'{players_online}')
    disp_name = str(client.user)[:-5] + " bot"

    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "steamuserinfo", description = "Gets user data from Steam website")
async def userid(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    try:
        info = steam.accountInfo(steam_token, username)
        bans = steam.accountBans(steam_token, username)
        if info[0] == 3:
            profileImage = info[4]
            profileImage_small = info[9]
            name = info[1]
            region = info[5]
            accountDate = info[2]
            gameCount = info[6]
            playtime = info[3]
            profile_url = info[8]
            online_status = info[7]
            embed=discord.Embed(title=f'Profile Link', url=profile_url, description=f'{name} {online_status}', color=0x0080ff)
            embed.set_author(name=f'{name} ({region})', icon_url=f'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/800px-Steam_icon_logo.svg.png')
            embed.add_field(name="Account Created", value=accountDate, inline=True)
            embed.add_field(name="Game Library", value=f'{gameCount} games', inline=True)
            embed.add_field(name="Total Playtime", value=f'{playtime} hours', inline=True)
            embed.add_field(name="VAC Bans?", value=f'{bans[2]}', inline=True)
            embed.add_field(name="Community Ban?", value=f'{bans[0]}', inline=True)
            embed.add_field(name="Trade Ban?", value=f'{bans[1]}', inline=True)
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

@tree.command(name = "championmastery", description = "Displays user's League of Legends champion mastery data")
async def championmastery(interaction: discord.Interaction, summoner_name: str, region: str):
    await interaction.response.defer()
    embed=discord.Embed(title=f'placeholder', url=f'', description=f'placeholder <:missing:720863696976347218>', color=0x0000ff)

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "championdata", description="Gets data for a League of Legends champion")
async def championdata(interaction: discord.Interaction, champion_name: str):
    await interaction.response.defer()
    championData = league.getChampionData(champion_name)

    embed=discord.Embed(title=f'Data for {championData[0]} {championData[1]}', description=f'{championData[2]}', color=0x0000ff)
    embed.add_field(name="Tags", value=f'{championData[5]}')
    embed.add_field(name="Resource Bar", value=f'{championData[7]}')
    embed.add_field(name="Tip", value=f'{str(championData[8])}')
    embed.set_thumbnail(url=championData[3])

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "weeklyrotation", description = "Gets League of Legends champions which are on the weekly rotation")
async def weeklyrotation(interaction: discord.Interaction):
    await interaction.response.defer()

    
    embed=discord.Embed(description=f'{league.getWeeklyRotation(riot_token)}', color=0x0000ff)

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

@tree.command(name = "leaguelivegame", description = "Gets live game data for a League of Legends player")
async def leaguelivegame(interaction: discord.Interaction, summoner_name: str, region: str):
    await interaction.response.defer()
    summoner_data = league.getSummonerData(summoner_name, region, riot_token)
    liveGameData = league.getLiveGame(riot_token, summoner_data[5], region, summonerEmoji)

    if liveGameData[0] == True:
        embed=discord.Embed(title=f'View on OP.GG (Spectate)', url=f'https://www.op.gg/summoners/{region}/{summoner_data[6]}/ingame', description=f'{summoner_data[0]} is playing {liveGameData[3]} in {liveGameData[2][1]} on {liveGameData[2][0]}', color=0x0000ff)
        
        embed.add_field(name="Summoner Spells", value=f'{liveGameData[6][0]} {liveGameData[6][1]}')
        embed.add_field(name="Banned Champions", value=f'{general.unpackList(liveGameData[4][0]) + general.unpackList(liveGameData[4][1])}')
        embed.set_author(name=f'{summoner_data[0]} ({region.upper()})', icon_url="https://static.wikia.nocookie.net/leagueoflegends/images/c/c0/LoL_ping_missing.png")
        
        embed.set_thumbnail(url=liveGameData[5])
        
        
    
    else:
        embed=discord.Embed(title="Summoner is not in game", description='', color=0x0000ff)
        embed.set_thumbnail(url="https://static.wikia.nocookie.net/leagueoflegends/images/c/c0/LoL_ping_missing.png")
    

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'{disp_name}')
    await interaction.followup.send(embed=embed)

# KAG Commands
@tree.command(name = "kagstats", description="Gets King Arthur's Gold Stats for a player")
async def kagstats(interaction: discord.Interaction, name: str):
    await interaction.response.defer()

    apiData = kag.getWebStatus()
    playerData = kag.getPlayerData(kag.searchPlayer(name))

    if playerData is not None and playerData[0] == True:
        #killData = kag.getPlayerStats(playerData[6])
        suicides, teamKills, archerStats, builderStats, knightStats, totalStats = playerData[6]
        embed=discord.Embed(title="KAGstats.com", url=playerData[7], description=f"Showing stats for {playerData[3]} {playerData[2]} ({playerData[1]})", color=0xFFD700)
        embed.set_thumbnail(url=playerData[5])
        embed.add_field(name=f"Archer ({round(archerStats[0]/archerStats[1], 2)})", value=f'{archerStats[0]} kills {archerStats[1]} deaths', inline=True)
        embed.add_field(name=f"Builder ({round(builderStats[0]/builderStats[1], 2)})", value=f'{builderStats[0]} kills {builderStats[1]} deaths', inline=True)
        embed.add_field(name=f"Knight ({round(knightStats[0]/knightStats[1], 2)})", value=f'{knightStats[0]} kills {knightStats[1]} deaths', inline=True)
        embed.add_field(name=f"Total ({round(totalStats[0]/totalStats[1], 2)})", value=f'{totalStats[0]} kills {totalStats[1]} deaths', inline=True)
        embed.set_author(name="kagstats api", icon_url="https://kagstats.com/favicon.ico")


    else:
        embed=discord.Embed(title="kagstats", url="https://kagstats.com", description=f"could not find user {name}", color=0xFFD700)

    disp_name = str(client.user)[:-5] + " bot"
    embed.set_footer(text=f'Tracking {apiData[1]} kills by {apiData[0]} across {apiData[2]} servers\n{disp_name} using KAGstats {apiData[3]}')
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