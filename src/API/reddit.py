from API.general import *


async def subsearch(subreddit: str, count: int=20, imageOnly: bool=True):
    """ Searches a given subreddit and returns an amount of post entries containing an image from the "Hot" section

    Parameters
    ----------
    subreddit : str
        Subreddit namelink
    count : int
        Amount of posts to load
    imageOnly : bool
        If true only returns posts with image attached (.png, .jpg, .gif etc)

    Returns
    -------
    postsOut : list
        List of tuples containing: title, description, author, post link, imagelink
    """
    posts = (await getJSON(f"https://www.reddit.com/r/{subreddit}/top.json?count={count}"))["data"]["children"]
    postsOut = []
    for post in posts:
        post = post["data"]
        try:
            if imageOnly == True:
                    if post ["post_hint"] == "image":
                        info = (post["title"], post["selftext"], post["author"], post["permalink"], post["url"])
                        postsOut.append(info)
            else:
                info = (post["title"], post["selftext"], post["author"], post["permalink"], post["url"])
                postsOut.append(info)
        except:
             pass
    return postsOut
