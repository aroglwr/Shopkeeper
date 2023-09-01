import json
import urllib.request as rq
import urllib.parse as qt
import os
from pathlib import Path
import datetime
from math import floor
from time import time

def getJSON(url):
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

def getJSON_filter(url):
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
    url_filter = qt.quote_plus(url, safe=":/?=!+")
    response = rq.urlopen(url_filter)
    data = json.load(response)
    return data

def getJSON_local(path):
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

def unpackList(list):
    string = ""
    for i in list:
        string += f'{i} '

    return string


def dateConvert(epochDate):
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
    formatted_date = date_time.strftime("%B %d, %Y, %I:%M %p %ZGMT,")
    formatted_date_alt = date_time.strftime("%B %d, %Y")
    return date_time, formatted_date, formatted_date_alt, date_time_alt



def timeElapsed(timestamp):

    dt1 = dateConvert(timestamp)[0]
    dt2 = dateConvert(floor(time()))[0]
    elapsed = dt2-dt1
    totalSeconds = elapsed.total_seconds()
    minutes, seconds = [floor(totalSeconds/60), round(totalSeconds%60)]

    return minutes, seconds

