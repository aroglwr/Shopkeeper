from API.general import *

async def apod(nasa_token, hd=False, random=False):
    if random:
        apod_data = await getJSON(f"https://api.nasa.gov/planetary/apod?api_key={nasa_token}&count=1")[0]
    else:
        apod_data = await getJSON(f"https://api.nasa.gov/planetary/apod?api_key={nasa_token}")
    try:
        title = apod_data["title"]
    except:
        title = "No title"
    try:
        desc = apod_data["explanation"]
    except:
        desc = "No description provided"
    date = apod_data["date"]
    try:
        author = apod_data["copyright"]
    except:
        author = "No author"
    if not hd:
        image = apod_data["url"]
    else:
        image = apod_data["hdurl"]


    return title, desc, date, author, image

async def earthImage(nasa_token):
    data = await getJSON(f"https://api.nasa.gov/EPIC/api/natural?api_key={nasa_token}")
    latest = data[-1]
    caption = latest["caption"]
    date_latest = latest["date"] # 2023-10-26
    image_id = latest["image"]
    image = f"https://api.nasa.gov/EPIC/archive/natural/{date_latest[:4]}/{date_latest[5:7]}/{date_latest[8:10]}/png/{image_id}.png?api_key={nasa_token}"


    return caption, date_latest, image


