import collections
from random import randint
import json
import requests
import praw
import requests_cache
from bs4 import BeautifulSoup
from app.content_management import league
from app.util import log

leagues = league()

r = praw.Reddit(user_agent="FootyLinks" + str(randint(0, 100000)))
subreddit = r.get_subreddit("footballhighlights")


FILTER_SIZE = 150


def get_highlights():
    # TODO - pass FILTER_SIZE as a **kwargs, set to 100 if none
    games = collections.OrderedDict({})                        # Use an OrderedDict to keep the order of the highlights

    for i, submission in enumerate(subreddit.get_hot(limit=FILTER_SIZE)):
        if "vs" in submission.title and "request" not in submission.title.lower():
            # if "request" not in submission.title.lower():
            split_name = submission.title.rsplit(' ', 1)
            date = split_name[1]
            game_name = split_name[0][:-1]

            for highlight in leagues:
                if highlight in submission.title and date[-4:] == "2017":               # Checking if the cup name exists in the title
                    name, h_league = parse_highlight_title(game_name, submission.title)
                    if name and h_league:
                        # Update the Ordered Dict with the details of the new game
                        games.update({str(i): [{
                                "highlight_name": name,
                                "game_date": date,
                                "submission_id": submission.id,
                                "highlight_league": h_league
                            }]
                        })

    return json.dumps(games), len(games)


def parse_highlight_title(game_name, t):
    try:
        # Parses the submission.title, try to account for all human errors (not reading subreddit rules...)
        if "–" in game_name:
            highlight_league = t[t.index('–') + 1: t.index(',')].strip()
            name = format_match_names(game_name[:game_name.index('–')])

        elif "-" in game_name:
            highlight_league = t[t.index('-') + 1: t.index(',')].strip()
            name = format_match_names(game_name[:game_name.index('-')])

        elif "," in game_name:
            first = t[t.index(',') + 1:]
            highlight_league = first[:first.index(',')].strip()
            name = format_match_names(game_name[:game_name.index(',')])

        else:
            # Post is not formatted properly so skip it
            name, highlight_league = '', ''

        return name, highlight_league

    except ValueError as e:
        log("Error msg: " + str(e))
        # Something went wrong in parsing the title (malformed or not valid) -> skip to the next title
        return False, False


def format_match_names(data):
    match = data.lower().split("vs")
    if len(match) > 1:
        home = match[0].strip().title()
        away = match[1].replace(".", "").replace(",", "").strip().title()

        return [home, away]

    else:
        return False


def parse_submission(reddit_id):
    links = []
    r_submission = r.get_submission(submission_id=reddit_id)
    html_tag = r_submission.selftext_html
    soup = BeautifulSoup(html_tag, "lxml")
    a_tags = soup.find_all("a")
    # print(a_tags)

    for i in range(len(a_tags)):
        link_title = a_tags[i].text.lower().replace('fullmatchesandshows', 'FMS')
        if i > 0 and ("fullmatchesandshows" in a_tags[i]['href'] or "highlightsfootball" in a_tags[i]['href']):
            # TODO - check why it has to be i > 0????
            links.append([link_title, find_links(a_tags[i]['href'] + str(i + 1))])
        else:
            links.append([link_title, find_links(a_tags[i]['href'])])

    return find_links(links)


def find_links(highlight_link):
    """
    Open link in a headless browser, parse HTML and extra video src, insert src into links page to remove ADs
    :param highlight_link: URL of the highlight
    :return: raw video src URL if found, else the normal URL
    """

    if "highlightsfootball" in highlight_link:
        final_link = highlightsfootball(highlight_link)

    elif "fullmatchesandshows" in highlight_link:
        final_link = fullmatchesandshows(highlight_link)

    elif "sportyhl" in highlight_link:
        final_link = sportyhl(highlight_link)

    elif "dailymotion" in highlight_link:
        final_link = dailymotion(highlight_link)

    elif "ourmatch" in highlight_link:
        final_link = ourmatch(highlight_link)

    elif "weshare" in highlight_link:
        final_link = weshare(highlight_link)

    elif "motdtv" in highlight_link:
        final_link = motdtvblogspot(highlight_link)

    elif "vid.me" in highlight_link:
        final_link = vidme(highlight_link)

    else:
        final_link = highlight_link

    # Return the link if found video
    if final_link is None:
        return highlight_link
    else:
        return final_link


def highlightsfootball(href):
    html = requests.get(href)
    soup = BeautifulSoup(html.content, "lxml")
    log(soup.prettify())

    # TODO - haven't been able to find a way around it for now


def fullmatchesandshows(href):
    build_link1 = "https://cdn.video.playwire.com/"
    build_link2 = "/videos/"
    build_link3 = "/video-sd.mp4"

    # Link to highlight request gets cached for 1 hour
    requests_cache.install_cache('fullmatchandshows_cache', expire_after=3600)

    html = requests.get(href)
    log("Highlights Cache - " + href + ": {0}".format(html.from_cache))
    soup = BeautifulSoup(html.content, "lxml")

    # Extracting the Video source and removing as many Ads as possible
    try:
        video_link = soup.find("script", {"src":"//cdn.playwire.com/bolt/js/zeus/embed.js"})
        link_content = video_link.get('data-config').split("/")
        full_link = build_link1 + link_content[3] + build_link2 + link_content[6] + build_link3

        return full_link
    except AttributeError:
        pass
        # log("Not from Playwire.com")

    try:
        return soup.find('div', {'class': 'spoiler'}).find_next_siblings('div')[0].iframe.get('data-lazy-src')
    except AttributeError:
        pass
        # log("Not from Streamable.com")

    try:
        vid = soup.find('div', {'class': 'acp_content'}).video.source.get('src')
        if "drive.google.com" not in vid:
            return vid
        else:
            return None
    except AttributeError:
        pass
        # log("Not an embedded Playwire URL")

    try:
        return soup.find('div', {'class': 'acp_content'}).find('iframe').get('data-lazy-src')
    except AttributeError:
        pass
        # log("Not an embedded link into an iframe...")

    return None         # Couldn't figure out how to get the video source, this shouldn't happen


def sportyhl(href):
    # Link to highlight request gets cached for 1 hour
    requests_cache.install_cache('sportyhl_cache', expire_after=3600)

    html = requests.get(href)
    log("Highlights Cache - " + href + ": {0}".format(html.from_cache))
    soup = BeautifulSoup(html.content, "lxml")

    vid = soup.find('iframe').get('src')

    return vid


def dailymotion(href):
    build_link1 = "http://www.dailymotion.com/embed/video/"
    build_link2 = "?autoplay=1"
    link_split = href.split("/")
    try:
        full_link = build_link1 + link_split[4] + build_link2
        return full_link
    except IndexError:
        pass
        # log("Error in size of href")
        return None


def ourmatch(href):
    build_link1 = "https://cdn.video.playwire.com/"
    build_link2 = "/videos/"
    build_link3 = "/video-sd.mp4"

    requests_cache.install_cache('ourmatch_cache', expire_after=3600)

    html = requests.get(href)
    log("Used Cache: {0}".format(html.from_cache))
    soup = BeautifulSoup(html.content, "lxml")
    try:
        video_link = soup.find("div", {"class":"video-tabs-labels"}).script.text
        video_link = video_link[video_link.index("cdn.video.playwire.com/"):video_link.index("/video-sd")].split("/")
        video_id1 = video_link[1]
        video_id2 = video_link[3]
        full_link = build_link1 + video_id1 + build_link2 + video_id2 + build_link3
        return full_link
    except:
        pass
        # log("OurMatch: No video link found")
        return None


def weshare(href):
    build_link1 = "https://weshare.me/services/mediaplayer/site/_embed.max.php?u="
    link_content = href.split("/")[3]
    full_link = build_link1 + link_content
    return full_link


def vidme(href):
    requests_cache.install_cache('vidme_cache', expire_after=3600)

    html = requests.get(href)
    log("Used Cache: {0}".format(html.from_cache))
    soup = BeautifulSoup(html.content, "lxml")
    try:
        full_link = soup.find("meta",{"name":"twitter:player:stream"}).get("content")
        return full_link
    except:
        pass
        # log("Vidme: No video link found")
        return None


def motdtvblogspot(href):
    requests_cache.install_cache('motdtvblogspot_cache', expire_after=3600)

    html = requests.get(href)
    log("Used Cache: {0}".format(html.from_cache))
    soup = BeautifulSoup(html.content, "lxml")
    try:
        full_link = soup.find("iframe").get('src')
        return full_link
    except:
        pass
        # log("MOTDTV: No video link found")
        return None



