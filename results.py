import argparse
from datetime import datetime
import json
import sys
import time

from prompt_toolkit import print_formatted_text, HTML
import pytz
from requests_html import HTMLSession
import schedule
from tabulate import tabulate
from yaspin import yaspin

import database

# color from https://en.wikipedia.org/wiki/X11_color_names
print = print_formatted_text

URL = 'https://www.livescore.cz/'
with open('livescore.json') as f:
    TABLE = json.load(f)['soccer']


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--print', '-p', action='store_true',
        help='print results in a nice table.')
    parser.add_argument(
        '--db', action='store_true',
        help='update events in the postgres db. Need configs.')
    parser.add_argument(
        '--json', type=str, default=None,
        help='save events results in the selected location as json.')
    parser.add_argument(
        '-s', '--schedule', type=int, default=30,
        help=('set the schedule time (default is 30 min). '
              'If set -1 run the job only one time'))
    args = parser.parse_args()
    print(HTML('<seagreen>✔</seagreen> args parsed'))
    return args


def pretty_print_events(events):
    headers = ['datetime', 'country', 'league', 'started', 'finished',
               'time', 'match']
    events_list = []
    for e in events:
        events_list.append([
            e['datetime'].strftime('%d %b \'%y - %H:%M'), e['country'],
            e["league"], f'{"✔" if e["started"] else "✘"}',
            f'{"✔" if e["finished"] else "✘"}', e['live_time'],
            (f'{e["home_team"]}  {e["home_goals"]} : '
             f'{e["away_goals"]}  {e["away_team"]}')
        ])
    table = tabulate(
        events_list, headers=headers, tablefmt='fancy_grid',
        colalign=(
            'center', 'left', 'left', 'center', 'center', 'center', 'center'))
    print(table)


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
        finished, started, live_time = False, False, None
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


def job(args):
    print('─' * 80)
    start_str = datetime.today().strftime(
        '%d %b %Y - %H:%M:%S').rjust(80 - len(' '.join(sys.argv[1:])))
    print(HTML(f'<teal>{" ".join(sys.argv[1:])}{start_str}</teal>\n'))
    with yaspin(text=f'scraping results') as sp:
        try:
            start_time = time.time()
            events = get_events()
            sp.hide()
            if args.db:
                database.update_events_in_db(events)
            if args.json is not None:
                database.save_results_in_json(events, args.json)
            if args.print and events:
                pretty_print_events(events)
            msg = ' got results'
            info = (f'{len(events)} events [{(time.time() - start_time):5.4}s]'
                    f'').rjust(79 - len(msg))
            print(HTML(f'<seagreen>✔</seagreen>' + msg + info))
        except IndexError as e:
            sp.hide()
            msg = f' [{type(e).__name__}]'
            print(HTML(f'<red>✘</red>' + msg))
        sp.show()


def main():
    args = parse_args()
    if args.schedule == -1:
        job(args)
    else:
        schedule.every(args.schedule).minutes.do(job, args=args)
        while True:
            schedule.run_pending()
            time.sleep(5)


if __name__ == '__main__':
    main()
