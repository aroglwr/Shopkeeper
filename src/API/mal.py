import requests
import xml.etree.ElementTree as ET

from API.general import getJSON



""" RSS FORMAT

rss version -> channel : title, link, description, 'items'

item -> title, link, desc, etc

"""

def mal_rss(username):
    var = requests.get(f"https://myanimelist.net/rss.php?type=rw&u={username}")
    rss = ET.fromstring(var.text)
    channel = rss[0]
    shows = []
    user = []
    
    anime_details = ["title", "link", "description", "pubDate"]
    user_details = ["title", "link", "description"]

    for detail in user_details:
        user.append(channel.findall(detail)[0].text)


    
    for entry in channel.findall("item"):
        show_info = []
        for detail in anime_details:
            show_info.append(entry.findall(detail)[0].text)
        shows.append(show_info)

    return user, shows

async def user_list(username, client_id):
    statuses = ["watching",  "on_hold", "dropped", "plan_to_watch", "completed"]
    count = {}
    watching =0
    completed=0
    on_hold=0
    dropped=0
    plan_to_watch=0

    header = {
                'X-MAL-CLIENT-ID': client_id
            }
    for status in statuses:

        params = {
                    'status':status
        }

        data = (await getJSON(url=f"https://api.myanimelist.net/v2/users/{username}/animelist?limit=1000", header=header, params=params))["data"]
        count[status] = len(data)
    
    anime_list =[]
    for entry in data:
        info = entry["node"]
        anime_list.append([info["title"], info["main_picture"]["large"]])
    #data = await getJSON(url=f"https://api.myanimelist.net/v2/users/{username}/animelist?limit=1000", header=header, params=params)
    
    return anime_list, count


async def anime_search(search, client_id):
    header = {'X-MAL-CLIENT-ID': client_id}
    params = {'q':search}
    data = (await getJSON(url="https://api.myanimelist.net/v2/anime", params=params, header=header))["data"]
    info = data[0]["node"]
    title =info["title"]
    img = info["main_picture"]["medium"]
    id = info["id"]
    return id 

async def anime_details(anime_id: int, client_id: str):
    """ Gets detailed information for specified anime from MyAnimeList

    Parameters
    ----------
    anime_id : int
        MyAnimeList ID (see `anime_search()`)
    client_id : str
        MyAnimeList client ID

    Returns
    -------
    name : str
        Official title
    description : str
        Synopsis
    episode_count : int
        Amount of episodes
    studios : list
        List of studios
    genres : list
        List of genres
    runtime : tuple
        (Start date, end date)
    users : int
        Amount of users with anime on their profile
    name_en : str
        English name
    name_jp : str
        Japanese name
    url : str
        Link to MAL page
    img : str
        URL to poster image
    
    """
    header = {'X-MAL-CLIENT-ID': client_id}
    
    data =await getJSON(url=f"https://api.myanimelist.net/v2/anime/{anime_id}?fields=id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,num_list_users,num_scoring_users,created_at,updated_at,media_type,status,genres,num_episodes,start_season,broadcast,source,rating,pictures,background,studios,statistics", header=header)
    #await saveJSON(url="https://api.myanimelist.net/v2/anime/40748?fields=id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,num_list_users,num_scoring_users,created_at,updated_at,media_type,status,genres,num_episodes,start_season,broadcast,source,rating,pictures,background,studios,statistics", header=header, filepath="src\\files\\mal.json")
    
    
    genres = []
    studios = []
    img = data["main_picture"]["medium"]
    for genre in data["genres"]:
        genres.append(genre["name"])
    for studio in data["studios"]:
        studios.append(studio["name"])
    name = data["title"]
    description = data["synopsis"]
    runtime = (data["start_date"], data["end_date"])
    users = data["num_list_users"]
    episode_count = data["num_episodes"]

    name_en = data["alternative_titles"]["en"]
    try:
        name_jp = data["alternative_titles"]["jp"]
    except:
        name_jp = data["alternative_titles"]["ja"]

    url = f"https://myanimelist.net/anime/{anime_id}/{name.replace(' ', '_')}"

    return name, description, episode_count, studios, genres, runtime, users, name_en, name_jp, url, img