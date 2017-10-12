import sys
import time
import gzip
import functools
import datetime
from io import BytesIO as IO
from flask import after_this_request, request


""" Global Helper Functions """


# Gzip (compression) for particular views (static content and responses)
# http://flask.pocoo.org/snippets/122/ - Updated for Python 3
def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Accept-Encoding', '')
            if 'gzip' not in accept_encoding.lower():
                return response

            response.direct_passthrough = False

            if response.status_code < 200 or response.status_code >= 300 or 'Content-Encoding' in response.headers:
                return response

            gzip_buffer = IO()
            gzip_file = gzip.GzipFile(mode='wb', fileobj=gzip_buffer)
            response.direct_passthrough = False
            gzip_file.write(response.data)
            gzip_file.close()

            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response
        return f(*args, **kwargs)
    return view_func


def log(message):
    """
    Print logs to heroku for debugging -> '$ heroku logs -t'
    :param message: string to be logged
    """
    print(str(message))
    sys.stdout.flush()


def gmt_time():
    """
    Get current GMT time
    """
    current_time = time.gmtime()
    # current_time = time.strftime('%a, %d %b %Y %H:%M:%S GMT', current_time)
    current_time = time.strftime('%H:%M GMT', current_time)

    return current_time


def compare_times(game_time):
    """
    Creates a status for each Live Stream
    :param game_time: GMT time
    :return: {String} Status: "Live", "Likely Expired", "Expired" and "Not Started"
    """
    # Format the different times
    game_time_formatted = game_time.replace("GMT", "").strip()
    current_time = gmt_time().replace("GMT", "").strip()

    # Create datetime objects
    g_time = datetime.datetime.strptime(game_time_formatted, '%H:%M')
    c_time = datetime.datetime.strptime(current_time, '%H:%M')

    # Get the difference in seconds
    result = (g_time - c_time).total_seconds() / 3600       # get the time difference in hours

    if result > 12:
        result -= 24                                        # Edge case - handle different days

    if -2 < result < 0:
        return "Live"
    elif -3 < result < -2:
        return "Likely Expired"
    elif -3 > result:
        return "Expired"
    elif result > 0:
        return "Not Started"


# print(gmt_time())
# print("\n")
# print(compare_times("22:50 GMT"))
# print(compare_times("23:50 GMT"))
# print(compare_times("00:50 GMT"))
