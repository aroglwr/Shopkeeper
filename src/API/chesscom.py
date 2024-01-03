from API.general import *


async def getUser(username: str):
    data = await getJSON(f"https://api.chess.com/pub/player/{username}")
    avatar = data.get("avatar", "https://cdn.discordapp.com/attachments/1042454661992558684/1180139196799778836/user-image.007dad08.png")
    title = data.get("title", "")
    if title != "":
        title = f"[{title}] "
    stream_url = data.get("twitch_url", "")
    url, displayname, country, last_online, joined, status, is_streamer, verified, league = data["url"], data["username"], data["country"], data["last_online"], data["joined"], data["status"], data["is_streamer"], data["verified"], data["league"]
    displayname = url[29:]
    return avatar, url, displayname, country, last_online, joined, status, is_streamer, verified, league, title, stream_url


async def getStats(username: str):
    stats = await getJSON(f"https://api.chess.com/pub/player/{username}/stats")
    realStats = []
    for stat in stats:
        if stat[:5] == "chess":
            statBlock = stats[stat]
            realStats.append((stat, [statBlock["last"]["rating"], statBlock["record"]["win"], statBlock["record"]["loss"], statBlock["record"]["draw"]]))
    return realStats