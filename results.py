from datetime import datetime
import json

import pytz
from requests_html import HTMLSession


URL = 'https://www.livescore.cz/'
with open('livescore.json') as f:
    TABLE = json.load(f)['soccer']


def parse_competition(row):
    _country, _league = row.text.split(' - ', 1)
    country = [k for k, v in TABLE.items() if v['name'] == _country]
    if len(country) == 1:
        country = country[0]
        league = [k for k, v in TABLE[country]['leagues'].items()
                  if v['name'] == _league]
        if len(league) == 1:
            league = league[0]
            if TABLE[country]['leagues'][league]['teams']:
                return country, league
    return None, None


def parse_event(row, country, league):
    dt = row.xpath('//td[@class="col-time nocol"]/time')[0].attrs['datetime']
    dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S%z').astimezone(pytz.utc)
    state = row.xpath('//td[@class="col-state nocol"]', first=True).text
    if state == '':
        finished, started, live_time = False, False, 0
    elif state[:-1].isdigit():
        finished, started, live_time = False, True, int(state[:-1])
    elif state == 'HT':
        finished, started, live_time = False, True, 45
    elif state == 'FT':
        finished, started, live_time = True, True, None
    _home_team = row.xpath('//td[@class="col-home"]', first=True).text
    _away_team = row.xpath('//td[@class="col-guest"]', first=True).text
    home_team = TABLE[country]['leagues'][league]['teams'][_home_team]
    away_team = TABLE[country]['leagues'][league]['teams'][_away_team]
    result = row.xpath('//td[@class="col-score"]')[0].text.replace('-', '0')
    home_goals, away_goals = [int(i) for i in result.split(':')]
    return {
        'datetime': dt,
        'country': country,
        'league': league,
        'finished': finished,
        'started': started,
        'live_time': live_time,
        'home_team': home_team,
        'away_team': away_team,
        'home_goals': home_goals,
        'away_goals': away_goals,
    }


def get_events():
    events = []
    session = HTMLSession()
    r = session.get(URL)
    table = r.html.xpath('//div[@id="soccer_livescore"]/table', first=True)
    rows = table.xpath('//tr')
    for row in rows:
        if row.attrs['class'][0] == 'tournament':
            country, league = parse_competition(row)
        elif (
            row.attrs['class'][0] == 'match' and
            (country, league) != (None, None)
        ):
            events.append(parse_event(row, country, league))
    return events


def main():
    [print(e) for e in get_events()]


if __name__ == '__main__':
    main()
