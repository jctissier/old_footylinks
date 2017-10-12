import os
import json
import requests
import requests_cache
from flask import Blueprint, request, render_template, make_response, jsonify
from app.stats.standings import Standings
from app.stats.fixtures import Fixtures
from app.stats.topstats import TopStats
import app.content_management as content
from app.util import log, gzipped


# Define the blueprint: 'highlights', set its url prefix: app.url/highlights
stat = Blueprint('stats', __name__, url_prefix='/stats/')


""" Fixtures Static Template """


@stat.route("fixtures", methods=['GET'])
@gzipped
def fixtures_load_page():
    """
    Static template for fixtures
    :return: HTML template
    """
    cards = content.cards()

    response = make_response(render_template("stats/fixtures.html", cards=cards))
    response.headers['Cache-Control'] = 'public, max-age=2628000'

    return response


""" Fixtures """


@stat.route('fixtures-ajax', methods=['POST'])
@gzipped
def fixtures_ajax():
    """
    AJAX requests to find fixtures
    :return: JSON response with the list of fixtures content
    """
    cache_db = "fixtures_cache.sqlite"
    requests_cache.install_cache('fixtures_cache', expire_after=1800)       # Cached for 15 mins

    if os.path.isfile(cache_db) and request.form.get('scheduler'):          # and value of league = epl? first one in the worker's recaching call
        log("Replacing Fixtures Cache")
        os.remove(cache_db)

    league = request.form['league']
    html = requests.get("https://footylinks.herokuapp.com/stats/rest-api/fixtures?league=" + league)
    log("Used Cache for Fixtures " + league + ": {0}".format(html.from_cache))

    try:
        fixtures = html.json()                              # Retrieve JSON string from GET request
    except json.JSONDecodeError:                            # If url/rest-api/highlights is down for some reason
        fixtures = Fixtures(league=league)                  # Provide content without caching
        fixtures = fixtures.get_fixtures()

    # Create Flask response and add headers to optimize delivery
    response = make_response(json.dumps(fixtures))
    response.headers['Cache-Control'] = 'public, max-age=1800'  # Cached for 15 min

    return response


@stat.route('rest-api/fixtures', methods=['GET'])
@gzipped
def fixtures_api():
    if request.args.get('league', None) is not None:
        league = request.args.get('league', None)
        fixtures = Fixtures(fixture=league)

        if fixtures.check_valid_league():
            return fixtures.get_fixtures()
        else:
            return jsonify({'status': 400, 'error': 'Wrong league argument found, Please try again.'})

    else:
        return jsonify({'status': 400, 'error': 'No league argument found. '
                                                'Format should be "/rest-api/fixtures?league=league_name"'})


""" Stats Static Template"""


@stat.route("home", methods=['GET'])
@gzipped
def stats_homepage():
    """
    Return information about a specific league: Standings, Top Scorers, Fixtures
    :return: Stats static template page HTML
    """
    response = make_response(render_template("stats/stat_home.html"))

    return response


""" Stats -> Standings """


@stat.route('standings-ajax', methods=['POST'])
@gzipped
def standings_ajax():
    """
    AJAX requests to find Standings
    :return: JSON response with the list of fixtures content
    """
    cache_db = "highlights_cache.sqlite"
    requests_cache.install_cache('standings_cache', expire_after=1800)              # Cached for 15 mins

    # request.form.get('scheduler')            # Make this true
    if os.path.isfile(cache_db) and request.form.get('scheduler'):
        log("Replacing Standings Cache")
        os.remove(cache_db)

    league = request.form['league']
    html = requests.get("https://footylinks.herokuapp.com/stats/rest-api/standings?league=" + league)
    log("Used Cache for Standings " + league + ": {0}".format(html.from_cache))

    try:
        standing = html.json()                                      # Retrieve JSON string from GET request
    except json.JSONDecodeError:                                    # If url/rest-api/highlights is down for some reason
        stats = Standings(league=league)                  # Provide content without caching
        standing = stats.get_standings()

    # Create Flask response and add headers to optimize delivery
    response = make_response(json.dumps(standing))
    response.headers['Cache-Control'] = 'public, max-age=1800'      # Cached for 15 min

    return response


@stat.route('rest-api/standings', methods=['GET'])
@gzipped
def standings_api():
    if request.args.get('league', None) is not None:
        league = request.args.get('league')
        standing = Standings(league=league)

        if standing.league_link is not None:
            return standing.get_standings()                                  # Already loaded into a JSON string
        else:
            return jsonify({'status': 400, 'error': 'Wrong league argument found, Please try again.'})

    else:
        return jsonify({
            'status': 400,
            'error': 'Missing the league argument, URL should look like "/rest-api/standings?league=league_name"'
        })


""" Stats -> Top Scorers & Top Assists """


@stat.route('topstats-ajax', methods=['POST'])
@gzipped
def topstats_ajax():
    """
    AJAX requests to find Top Scorers & Assists
    :return: JSON response with the list of top scorers & assists
    """
    league = request.form['league']
    scorer = TopStats(league=league, scorer=True)
    assist = TopStats(league=league, assist=True)

    return jsonify({
            'scorers': scorer.get_topstats(),
            'assists': assist.get_topstats()
         })


@stat.route('rest-api/topstats', methods=['GET'])
@gzipped
def topstats_api():
    if request.args.get('league', None) is not None:
        league = request.args.get('league')
        scorer = TopStats(league=league, scorer=True)
        assist = TopStats(league=league, assist=True)

        if scorer.league_name is not None and assist.league_name is not None:
            return jsonify({
                'scorers': scorer.get_topstats(),
                'assists': assist.get_topstats()
            })

        # One or both of the league arguments were not valid
        else:
            return jsonify({'status': 400, 'error': 'Wrong league argument found, Please try again.'})

    else:
        # No league arguments were included in the request
        return jsonify({
            'status': 400,
            'error': 'Missing the league argument, URL should look like "/rest-api/topstats?league=league_name"'
        })
