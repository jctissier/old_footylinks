import collections
import json
import requests
import requests_cache
from bs4 import BeautifulSoup
from app.util import log


# TopScorer request gets cached for 1 hour
# requests_cache.install_cache('get_topscorer', expire_after=7200)


class TopStats(object):
    """
    Retrieve Top Scorers or Top Assists about a specific league/competition
    """
    PRE_LINK = "http://www.espnfc.us/"
    POST_LINK = "/statistics/"

    def __init__(self, league, **kwargs):
        if self.league_map(league) is not None:
            self.league_name = self.league_map(league)
        else:
            self.league_name = None
        self.scorer = kwargs.get('scorer', False)                   # Should only be 1 per class instance
        self.assist = kwargs.get('assist', False)

    def get_topstats(self):
        """
        Generate JSON with Top Scorers & Assists for a specific league/competition
        :return: JSON string
        """
        if self.scorer:
            html = requests.get(self.PRE_LINK + self.league_name + self.POST_LINK + "scorers")
        elif self.assist:
            html = requests.get(self.PRE_LINK + self.league_name + self.POST_LINK + "assists")

        # log("Used Cache: {0}".format(html.from_cache))
        soup = BeautifulSoup(html.content, "lxml")

        try:
            c = soup.find('div', {'class': 'stats-top-scores'}).table.find_all('td')
            data = collections.OrderedDict({})

            for x, i in enumerate(range(0, len(c), 4)):
                if i < 40:                                      # Gets the top 10 players (4 td's per row)
                    # update the dict with scraped content
                    data.update({str(x + 1): [{
                            "rank": x + 1,
                            "name": c[i + 1].text.strip(),
                            "club": c[i + 2].text.strip(),
                            "total": c[i + 3].text.strip()
                        }]
                    })

            return json.dumps(data)

        except AttributeError as e:
            log('No Table found in TopStats ==> ' + str(e))
            return False

    @staticmethod
    def league_map(league):
        leagues = {
            'epl': 'english-premier-league/23',
            'liga': 'spanish-primera-division/15',
            'bundesliga': 'german-bundesliga/10',
            'ligue1': 'french-ligue-1/9',
            'seriea': 'italian-serie-a/12'
        }

        return leagues.get(league)


# Creating a Top Stats object instance
# if __name__ == "__main__":
#     test = TopStats(league="ligue1", assist=True)
#     test.get_topstats()
