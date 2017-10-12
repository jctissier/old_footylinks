import collections
import re
from random import randint
import json
import praw

from app.util import log


r = praw.Reddit(user_agent="FootyLinks" + str(randint(0, 100000)))
subreddit = r.get_subreddit("soccerstreams")

FILTER_SIZE = 50


def parse_stream_title(title, has_time):
    """
    Parses the post title to extract game time and name (if exists)
    :param title: submission.title
    :param has_time: true if "GMT" in title, false otherwise
    :return: formatted game time and game name
    """
    try:
        # Parses the submission.title, try to account for all human errors (not reading subreddit rules...)
        if has_time:
            game_name = title[title.index(']') + 1:].strip()
            game_time = title[:title.index(']') + 1].strip().replace("[", "").replace("]", "")
            print(game_time, game_name)
        elif not has_time:
            game_name = title
            game_time = ''
        else:
            # Stream post is not formatted properly so skip it
            game_time, game_name = '', ''

        return game_time, game_name

    except ValueError as e:
        # Something went wrong in parsing the title (malformed or not valid) -> skip to the next title
        log("Error msg: " + str(e))
        return False, False


def get_streams():
    """
    Extracts list of current live streams
    :return: JSON formatted list of live streams, size of the list
    """
    streams = collections.OrderedDict({})                     # Use an OrderedDict to keep the order of the streams

    for i, submission in enumerate(subreddit.get_hot(limit=FILTER_SIZE)):
        if "vs" in submission.title.lower():

            if "GMT" in submission.title:           # Parse the title and extra game time and name
                game_time, game_name = parse_stream_title(title=submission.title, has_time=True)
            else:
                game_time, game_name = parse_stream_title(title=submission.title, has_time=False)

            if game_time and game_name:             # if time and name not false
                # Update the Ordered Dict with the details of the stream
                streams.update({str(i): [{
                        "game_name": game_name,
                        "game_time": game_time,
                        "submission_id": submission.id,
                        "competition": submission.selftext
                    }]
                })

    print(json.dumps(streams), len(streams))
    # return json.dumps(streams), len(streams)

# get_streams()


def parse_submission(reddit_id):
    """
    Extracts stream links from top 10 comment of the post
    :param reddit_id: specific reddit post in r/soccerstreams
    :return: JSON formatted list of stream links for a particular match, size of the list
    """
    regex = r"\[(.*?)\]\((.*?)\)"                                   # Extracts markdown hyperlinks + names
    r_submission = r.get_submission(submission_id=reddit_id)
    stream_links = collections.OrderedDict({})

    for i, comment in enumerate(r_submission.comments[:10]):
        matches = re.findall(regex, comment.body)
        for link in matches:
            stream_links.update({str(i): [{
                    "stream_title": link[0],
                    "stream_link": link[1],
                    "upvotes": comment.score
                }]
            })

    print(json.dumps(stream_links), len(stream_links))

# parse_submission('74gk2b')
