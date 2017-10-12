import collections
import os.path
from datetime import datetime, timedelta
import json
import requests
import requests_cache
from bs4 import BeautifulSoup
from flask import jsonify
from app.util import log


# Fixtures request gets cached for 12 hour
# requests_cache.install_cache('get_fixtures', expire_after=43200)


class Fixtures(object):
    """
    Retrieve fixtures about a specific league/competition
    Options:
        England
            premierleague
            fa-cup
            efl-cup

        Competitions
            championsleague
            uefa-europa-league

        Leagues
            laligafootball
            ligue1football
            bundesligafootball
            serieafootball

        International
            euro-2016-qualifiers
            friendlies
            copa-america
            world-cup-2018
    """
    PRE_LINK = "https://www.theguardian.com/football/"
    POST_LINK = "/fixtures"
    CACHE_DB = 'get_fixtures.sqlite'
    CHOICES = ['euro-2016-qualifiers', 'world-cup-2018-qualifiers', 'friendlies', 'serieafootball', 'bundesligafootball',
               'ligue1football', 'laligafootball', 'uefa-europa-league', 'champions-league-qualifying', 'premierleague']

    def __init__(self, fixture, **kwargs):
        self.fixture_name = fixture
        # self.scheduled_job = kwargs.get('scheduler', False)

    def get_fixtures(self):
        """
        Generate dynamic JSON with upcoming fixtures about a specific league/competition
        :return: JSON content
        """
        # If request is coming in for scheduler job (cached results) and db still exists and it's element 1 in list:
        #   - remove db file and re-cache request
        # if self.scheduled_job and self.fixture_name == "premierleague":
        #     log("In cache removal!")
        #     if os.path.isfile(self.CACHE_DB):
        #         log("Removing cache")
        #         os.remove(self.CACHE_DB)

        # Check if cache file exists
        # log("Fixtures Cache Exists Pre-Request: {0}".format(os.path.isfile(self.CACHE_DB)))

        html = requests.get(self.PRE_LINK + self.fixture_name + self.POST_LINK)

        # Check if cache was used & if the cache file exists (True True or False False)
        # log("Used Cache: {0}".format(html.from_cache))
        # log("File Exists Post-Cache: {0}".format(os.path.isfile(self.CACHE_DB)))

        soup = BeautifulSoup(html.content, "lxml")
        divs = soup.find_all('div', {'class': 'football-matches__day'})

        if len(divs) != 0:
            data = collections.OrderedDict({})

            for i, date in enumerate(divs):
                if i < len(divs):
                    game_date = date.find('div', {'class': 'date-divider'}).text

                    # for each 'tr' extract all of the td's and extract what's necessary
                    temp_data = []
                    for x, game in enumerate(date.find_all('tr')):
                        if x > 0:
                            temp_data.append(self.extract_games_per_gameday(game))

                    # update the dict with scraped content
                    data.update({str(i): [{
                            "no_games": str(len(date.find_all('tr')) - 1),
                            "game_date": game_date.replace('2017', '').strip(),
                            "content": temp_data
                        }]
                    })

            return json.dumps(data)

        else:
            # if there are no games scheduled
            return jsonify({'status': 200, 'message': 'No Fixtures were found. Try again later.', 'error': True})

    def check_valid_league(self):
        return True if self.fixture_name in self.CHOICES else False

    def extract_games_per_gameday(self, data):
        """
        Extract relevant data from each game divs
        :param data:
            # - date of game            --> td[0]           Scraping Vancouver time, need UTC+1 for europe
            # - home team crest         --> td[1]
            # - home team name          --> td[2]
            # - away team name          --> td[2]
            # - away team crest         --> td[3]
        :return: String (game date, home logo, home team, away team, away logo)
        """
        game_detail = data.find_all('td')

        g_date = self.get_game_date(game_detail[0])
        h_crest = self.get_team_crests(game_detail[1])
        h_name, a_name = self.get_team_names(game_detail[2])
        a_crest = self.get_team_crests(game_detail[3])

        return g_date, h_crest, h_name, a_name, a_crest

    @staticmethod
    def get_game_date(game_date):
        """
        Extract game's date and time
        """
        extract_date = game_date.time.get('datetime')       # parse this
        date = extract_date.split('T')[1].split('+')[0]
        game = datetime.strptime(date, "%H:%M:%S") + timedelta(hours=-8)        # Converts to Vancouver Time

        return str(format(game, "%H:%M %p"))

    @staticmethod
    def get_team_names(game_info):
        """
        Extract team names
        """
        team_names = game_info.find_all('span')
        h_name = team_names[0].text
        a_name = team_names[1].text

        return h_name, a_name

    @staticmethod
    def get_team_crests(team_crest):
        """
        Extract team logo
        """
        return team_crest.span.get('style')[22:-2]          # extract team logo


# Creating a Fixture object instance
# if __name__ == "__main__":
#     test = Fixtures(fixture="premierleague", scheduler=True)
#     test.get_fixtures()
