from API.general import *

async def apod_old(nasa_token, hd=False, random=False):
    """ LEGACY VERSION USE apod() INSTEAD"""
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
async def apod(nasa_token, hd=False, random=False):
    """ Get astro photo of the day from NASA
    
    Parameters
    ----------
    nasa_token : str
        NASA API token
    hd : bool
        Return HD image or not
    random : bool
        Return random APOD, when false returns todays
    
    Returns
    -------
    title : str
        Title of APOD (Can be empty)
    desc : str
        Description of APOD (Can be empty)
    date : str
        Publish date of APOD (Can be empty)
    author : str
        Author of APOD image (Can be empty)
    image : str
        URL to APOD image
    """
    apod_data = await getJSON(f"https://api.nasa.gov/planetary/apod?api_key={nasa_token}" + ("&count=1" if random else ""))
    if random:
        apod_data = apod_data[0]
    title = apod_data.get("title", "No title")
    desc = apod_data.get("explanation", "No description provided")
    date = apod_data.get("date", "")
    author = apod_data.get("copyright", "No author")
    image = apod_data.get("hdurl" if hd else "url", "")
    return title, desc, date, author, image

async def earthImage(nasa_token):
    """ DEPRECATED FUNCTION """
    data = await getJSON(f"https://api.nasa.gov/EPIC/api/natural?api_key={nasa_token}")
    latest = data[-1]
    caption = latest["caption"]
    date_latest = latest["date"] # 2023-10-26
    image_id = latest["image"]
    image = f"https://api.nasa.gov/EPIC/archive/natural/{date_latest[:4]}/{date_latest[5:7]}/{date_latest[8:10]}/png/{image_id}.png?api_key={nasa_token}"


    return caption, date_latest, image


