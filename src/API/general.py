import json
import urllib.request as rq
import urllib.parse as qt
import os
import platform
from pathlib import Path
import datetime
from math import floor
from time import time

def getJSON(url: str):
    """ Simple get JSON file from URL

    Parameters
    ----------
    url : str
        URL of json file
    
    Returns
    -------
    data : dict
        Dictionary of JSON components
    
    """
    response = rq.urlopen(url)
    data = json.load(response)
    return data

def getJSON_filter(url: str):
    """ Simple get JSON file from URL with filter

    Parameters
    ----------
    url : str
        URL of json file
    
    Returns
    -------
    data : dict
        Dictionary of JSON components
    
    """
    url_filter = qt.quote_plus(url, safe=':/?=!+&"[{}],')
    response = rq.urlopen(url_filter)
    data = json.load(response)
    return data

def getJSON_local(path: str):
    """ Simple get JSON file from relative local path

    Parameters
    ----------
    url : str
        URL of json file
    
    Returns
    -------
    data : dict
        Dictionary of JSON components
    
    """
    path = os.path.abspath(path)
    p = Path(path)
    output = getJSON(p.as_uri())
    return output

def unpackList(list: list, comma: bool):
    string = ""
    if comma == True:
        for word in list:
                if word != list[len(list)-1]:
                    string += word + ", "
                else:
                    string += word
    else:
        for word in list:
            string += f'{word} '

    return string


def dateConvert(epochDate: int):
    """ Converts timestamp from epoch to standard

    Parameters
    ----------
    epochDate : int
        Date in epoch form

    Returns
    -------
    date_time : datetime obj
        Formatted for datetime package
    
    formatted_date : str
        Timestamp in nice format
    
    formatted_date_alt : str
        Alternative version of formatted_date
    
    date_time_alt : str
        Alternative datetime obj
    """
    date_time = datetime.datetime.fromtimestamp(epochDate)
    date_time_alt = date_time.strftime("%Y-%m-%d")
    formatted_date = date_time.strftime("%B %d, %Y, %I:%M %p %ZUTC,")
    formatted_date_alt = date_time.strftime("%B %d, %Y")
    return date_time, formatted_date, formatted_date_alt, date_time_alt



def timeElapsed(timestamp: int):

    dt1 = dateConvert(timestamp)[0]
    dt2 = dateConvert(floor(time()))[0]
    elapsed = dt2-dt1
    totalSeconds = elapsed.total_seconds()
    minutes, seconds = [floor(totalSeconds/60), round(totalSeconds%60)]

    return minutes, seconds

def getVersion():
    return platform.python_version()

def progressBar(length: int, percentage: float):

    
    show = int(round((percentage)*length, 0))
    string = ""
    for x in range(length):
        string += "#"
    bar = string[:show]
    for i in range(length-show):
        bar += ("-")
    
    return bar