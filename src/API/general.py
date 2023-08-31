import json
import urllib.request as rq
import urllib.parse as qt
import os
from pathlib import Path


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