import requests
import json
import os
import requests_cache
from flask import Blueprint, request, render_template, make_response, jsonify
import app.highlights.models as highlights
from app.util import log, gzipped, gmt_time


# Define the blueprint: 'highlights', set its url prefix: app.url/highlights
highlight = Blueprint('highlights', __name__)


""" Find Highlights """


@highlight.route('/')
@highlight.route('/highlights', methods=['GET'])
@gzipped
def load_page():
    """
    Skeleton of Highlights page
    :return: Highlights template (static HTML)
    """
    response = make_response(
        render_template("highlights/highlight.html")
    )
    response.headers['Cache-Control'] = 'public, max-age=2628000'           # 1 month

    return response


@highlight.route('/highlights-ajax', methods=['POST'])
@gzipped
def load_ajax():
    """
    AJAX requests to retrieve highlights from Reddit API
    :return: JSON response with the list of highlights content
    """
    cache_db = "highlights_cache.sqlite"
    requests_cache.install_cache('highlights_cache', expire_after=600)          # Cached for 15 mins

    if os.path.isfile(cache_db) and len(request.get_data()) > 0:
        log("Replacing Highlights Cache at: " + str(gmt_time()))
        os.remove(cache_db)

    html = requests.get("https://footylinks.herokuapp.com/rest-api/highlights")     # cache DB is created on requests
    log("Used Cache for Highlights: {0}".format(html.from_cache))

    try:
        json_highlights = html.json()                              # Retrieve JSON string from GET request
    except json.JSONDecodeError:                                   # If url/rest-api/highlights is down for some reason
        highlights_data, size = highlights.get_highlights()        # Provide content without caching
        json_highlights = {
            'highlights': highlights_data,
            'size': size
        }

    # Create Flask response and add headers to optimize delivery
    response = make_response(jsonify({
            'success': 200,
            'list': json_highlights['highlights'],
            'size': json_highlights['size']
        }))
    response.headers['Cache-Control'] = 'public, max-age=600'

    return response


""" REST API endpoint """


@highlight.route('/rest-api/highlights', methods=['GET'])
@gzipped
def highlights_json():
    highlights_data, size = highlights.get_highlights()

    return jsonify({
            'highlights': highlights_data,
            'size': size
        })


""" Find Highlights Links """


@highlight.route("/link", methods=['GET'])
@gzipped
def highlight_links():
    if request.args.get('post_id', False) is not False:
        reddit_link = request.args.get('post_id', False)
        game_title = request.args.get('title', False)
        comp = request.args.get('comp', False)
        date = request.args.get('date', False)

    response = make_response(
        render_template("highlights/links.html", links_page=True,
                        reddit_link=reddit_link, game_title=game_title,
                        competition=comp, date=date)
    )
    response.headers['Cache-Control'] = 'public, max-age=3600'

    return response


@highlight.route('/link-retrieval', methods=['GET'])
@gzipped
def ajax_get_links():
    if request.args.get('post_id', False) is not False:
        reddit_link = request.args.get('post_id')
        final_links = highlights.parse_submission(reddit_link)
        log(final_links)

    else:
        final_links = False

    return jsonify({
        'links': final_links
    })
