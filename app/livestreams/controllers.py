from flask import Blueprint, request, render_template, make_response, jsonify, session, g, redirect, url_for
import json
import os
import requests
import requests_cache
import app.livestreams.models as livestreams
from app.util import log, gzipped, gmt_time


# Define the blueprint: 'highlights', set its url prefix: app.url/highlights
livestream = Blueprint('livestreams', __name__)


""" Find Live Streams """


@livestream.route('/livestreams', methods=['GET'])
@gzipped
def load_page():
    """
    Skeleton of Livestreams page
    :return: Livestreams template (static HTML)
    """
    response = make_response(
        render_template("livestreams/livestreams.html")
    )
    response.headers['Cache-Control'] = 'public, max-age=2628000'               # 1 month

    return response


@livestream.route('/livestreams-ajax', methods=['POST', 'GET'])
@gzipped
def load_ajax():
    """
    AJAX requests to retrieve livestreams from Reddit API
    :return: JSON response with the list of livestreams matches
    """
    cache_db = "livestreams_cache.sqlite"
    requests_cache.install_cache('livestreams_cache', expire_after=600)          # Cached for 10 mins

    if os.path.isfile(cache_db) and len(request.get_data()) > 0:
        log("Replacing Livestreams Cache at: " + str(gmt_time()))
        os.remove(cache_db)

    html = requests.get("https://footylinks.herokuapp.com/rest-api/livestreams")     # cache DB is created on requests
    log("Used Cache for Livestreams: {0}".format(html.from_cache))

    try:
        json_livestreams = html.json()                              # Retrieve JSON string from GET request
    except json.JSONDecodeError as e:
        log("JSON DECODE ERROR Caught - Not cached")
        streams_data, size = livestreams.get_streams()
        json_livestreams = {
            'livestreams': streams_data,
            'size': size
        }

    # Create Flask response and add headers to optimize delivery
    response = make_response(jsonify({
            'success': 200,
            'list': json_livestreams['livestreams'],
            'size': json_livestreams['size'],
            'gmt_time': gmt_time()
    }))
    response.headers['Cache-Control'] = 'public, max-age=600'

    return response


@livestream.route('/gmt-ajax', methods=['POST'])
def get_gmt():
    """
    Get current GMT time
    :return: JSON response with current formatted GMT time
    """
    return jsonify({'gmt_time': gmt_time()})


""" Find Stream Links """


@livestream.route('/livestreams/link', methods=['POST'])
@gzipped
def livestream_links():
    post_id = request.form['post_id']

    # cache_db = "livestreams_links_cache.sqlite"
    requests_cache.install_cache('livestreams_links_cache', expire_after=600)  # Cached for 10 mins

    # if os.path.isfile(cache_db) and len(request.get_data()) > 0:
    #     print("Replacing Livestreams Links Cache")
    #     os.remove(cache_db)

    html = requests.get("https://footylinks.herokuapp.com/rest-api/livestreams/links?post_id=" + post_id)
    print("Used Cache for Livestreams Links: {0}".format(html.from_cache))

    try:
        links_to_stream = html.json()                # Retrieve JSON string from GET request
    except json.JSONDecodeError:
        stream_links, size = livestreams.parse_submission(reddit_id=post_id)
        links_to_stream = {
            'links': stream_links,
            'size': size
        }

    # Create Flask response and add headers to optimize delivery
    response = make_response(jsonify({
            'status': 200,
            'links': links_to_stream['links'],
            'size': links_to_stream['size']
        }))
    response.headers['Cache-Control'] = 'public, max-age=600'

    return response


""" REST API endpoint """


@livestream.route('/rest-api/livestreams', methods=['GET'])
@gzipped
def livestreams_json():
    streams_data, size = livestreams.get_streams()

    return jsonify({
        'livestreams': streams_data,
        'size': size,
        'gmt_time': gmt_time()
    })


@livestream.route('/rest-api/livestreams/links', methods=['GET'])
@gzipped
def livestreams_links_json():
    try:
        post_id = request.args.get('post_id')
        stream_links, size = livestreams.parse_submission(reddit_id=post_id)

        return jsonify({
            'links': stream_links,
            'size': size
        })
    except TypeError:
        return jsonify({'status': 400, 'err': 'GET request is missing parameter post_id: '
                        'e.g. https://footylinks.herokuapp.com/rest-api/livestreams/links?post_id='})
