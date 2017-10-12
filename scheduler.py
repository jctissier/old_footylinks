from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import sys

# TODO
# Replace this with the simple scheduler
# Run multiple jobs (all free anyways)

FOOTYLINKS = "http://footylinks.herokuapp.com/stats/rest-api/fixtures?league="

scheduler = BlockingScheduler()


@scheduler.scheduled_job('interval', minutes=1440, misfire_grace_time=None)
def fixtures_scheduler():
    """
    Main scheduler for Footylinks, pings the app to cache requests and deliver faster response time for users
    """
    fixtures_caching()


@scheduler.scheduled_job('interval', minutes=10, misfire_grace_time=None)
def content_scheduler():
    """
    Cached requests for highlights, JSON response from PRAW reddit API
    """
    highlights_caching()
    livestreams_caching()


"""
    Scheduler helper functions
"""


def fixtures_caching():
    """
    Re-caches fixtures content every 24 hours
    """
    pings = [
        "premierleague", "championsleague", "uefa-europa-league", "world-cup-2018-qualifiers",
        "friendlies", "serieafootball", "bundesligafootball", "ligue1football", "laligafootball"
             ]

    for i in range(len(pings)):
        requests.get(url=FOOTYLINKS + pings[i])
        log("****** Fixtures Caching Job ******" + pings[i])


def highlights_caching():
    """
    Re-caches content for highlights every 10 minutes
    """
    cached = requests.post(url="https://footylinks.herokuapp.com/highlights-ajax", data={'cached': 1})
    log("****** Highlights Caching Job ******" + str(cached))


def livestreams_caching():
    """
    Re-caches content for live streams every 10 minutes
    """
    cached = requests.post(url="https://footylinks.herokuapp.com/livestreams-ajax", data={'cached': 1})
    log("****** Livestreams Caching Job ******" + str(cached))


def log(message):
    """
    Print logs to heroku for debugging -> '$ heroku logs -t'
    :param message: value that will be printed
    """
    print(str(message))
    sys.stdout.flush()


scheduler.start()
