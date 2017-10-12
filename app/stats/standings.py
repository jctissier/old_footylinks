import collections
import json
import requests
# import requests_cache
from bs4 import BeautifulSoup
from app.util import log


# Standings request gets cached for 1 hour
# requests_cache.install_cache('get_standings', expire_after=43200)


class Standings(object):
    """
    Retrieve Standings about a specific league/competition
    """
    PRE_LINK = "http://ca.soccerway.com/"

    def __init__(self, league):
        if self.league_map(league) is not None:
            self.league_link = self.league_map(league)
        else:
            self.league_link = None

    def get_standings(self):
        """
        Generate dynamic JSON with upcoming standings about a specific league/competition
        :return: JSON content
        """
        html = requests.get(self.PRE_LINK + self.league_link)
        print(self.PRE_LINK + self.league_link)
        # log("Used Cache: {0}".format(html.from_cache))
        soup = BeautifulSoup(html.content, "lxml")
        tbody = soup.find('table').find('tbody').find_all('tr')

        data = collections.OrderedDict({})
        for x, row in enumerate(tbody):
            temp = self.parse_rows(row)
            data.update({str(x + 1): {
                    "rank": temp[0],
                    "name": temp[1],
                    "mp": temp[2],
                    "w": temp[3],
                    "d": temp[4],
                    "l": temp[5],
                    "gd": temp[6],
                    "pts": temp[7],
                    "form": temp[8]
                }
            })

        return json.dumps(data)

    def get_league(self):
        return self.league_link

    @staticmethod
    def league_map(league):
        """
        Maps the proper league url
        """
        find_link = {
            'epl': 'national/england/premier-league/20172018/regular-season/r41547/',
            'seriea': 'national/italy/serie-a/20172018/regular-season/r42011/',
            'liga': 'national/spain/primera-division/20172018/regular-season/r41509/',
            'ligue1': 'national/france/ligue-1/20172018/regular-season/r41646/',
            'bundesliga': 'national/germany/bundesliga/20172018/regular-season/r41485/'
        }

        return find_link.get(league)

    def parse_rows(self, row):
        """
        Extract content from each row of the table
        """
        row_content = row.find_all('td')

        rank = self.extract_text(row_content[0])
        name = self.extract_text(row_content[2])
        played = self.extract_text(row_content[3])
        win = self.extract_text(row_content[4])
        draw = self.extract_text(row_content[5])
        loss = self.extract_text(row_content[6])
        gd = self.extract_text(row_content[9])
        points = self.extract_text(row_content[10])
        form = self.extract_form(row_content[11])

        return [rank, name, played, win, draw, loss, gd, points, form]

    @staticmethod
    def extract_text(row):
        """
        Extract the text from HTML
        """
        return row.text.strip()

    @staticmethod
    def extract_form(form):
        past_form = form.find_all('a')

        all_form = []
        for game in past_form:
            results = game.get('title').split('-', 1)
            home = results[0].strip()
            away = results[1][:-5].strip()
            score = results[1][-5:]
            date = game.get('href').split('/')
            all_form.append([game.text, home + " " + score + " " + away, date[4] + "-" + date[3] + "-" + date[2]])

        return all_form

# Creating a Standings object instance
# if __name__ == "__main__":
#     test = Standings(league="epl")
#     test.get_standings()

