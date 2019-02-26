import argparse
import csv
import datetime
import os
import sys
import time

from prompt_toolkit import print_formatted_text, HTML
import schedule
from yaspin import yaspin

from aao.spiders import spiders
import database

# color from https://en.wikipedia.org/wiki/X11_color_names
print = print_formatted_text


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'bookmaker', type=str,
        choices=spiders.keys(),
        help='choose the bookmaker')
    parser.add_argument(
        '--notheadless', action='store_false',
        help='run spider in not headless mode')
    parser.add_argument(
        '--db', action='store_true',
        help='save events and odds in a postgres db. Need configs.')
    parser.add_argument(
        '--json', type=str, default=None,
        help='save events and odds in the selected location as json.')
    parser.add_argument(
        '--log', default='CRITICAL',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='set console log level')
    parser.add_argument(
        '-s', '--schedule', type=int, default=60,
        help=('set the schedule time (default is 60 min). '
              'If set -1 run the job only one time'))
    parser.add_argument(
        '-d', '--delay', type=int, default=0,
        help=('set a delay for the initial scrape (default is 0 min)'))
    parser.add_argument(
        '-p', '--proxy', type=str, default=None,
        help=('use proxy in selenium for avoinding country ban. '
              'e.g https://123.123.13:71 [type]://[host]:[port]'))
    parser.add_argument(
        '-u', '--username', type=str, default=None,
        help=('some spider require username to login.'))
    parser.add_argument(
        '-pw', '--password', type=str, default=None,
        help=('some spider require password to login.'))
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help='quiet output. Do not print sensible data')
    args = parser.parse_args()
    print(HTML('<seagreen>✔</seagreen> args parsed'))
    return args


def get_competitions(bookmaker):
    here = os.path.dirname(os.path.realpath(__file__))
    directory = os.path.join(here, 'competitions')
    file = os.path.join(directory, f'{bookmaker}.csv')
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        competitions = [[row[0], row[1]]for row in reader]
    print(HTML(
        f'<seagreen>✔</seagreen> found {len(competitions)} competitions'))
    for c in competitions:
        print(f'  • {c[0]} - {c[1]}')
    return competitions


def job(args, competitions):
    sys.stdout.write('\r' + '─' * 80 + '\n')
    sys.stdout.flush()
    start_str = datetime.datetime.today().strftime(
        '%d %b %Y - %H:%M:%S').rjust(80 - len(' '.join(sys.argv[1:])))
    if not args.quiet:
        print(HTML(f'<teal>{" ".join(sys.argv[1:])}{start_str}</teal>\n'))
    try:
        spider = spiders[args.bookmaker](
            username=args.username,
            password=args.password,
            headless=args.notheadless,
            proxy=args.proxy,
            console_level=args.log,
        )
        for i, [country, league] in enumerate(competitions):
            with yaspin(text=f'scraping {country} - {league}') as sp:
                try:
                    start_time = time.time()
                    events, odds = spider.soccer.odds(country, league)
                    if args.db:
                        database.save_events_odds_in_db(
                            events, odds, args.bookmaker)
                    if args.json is not None:
                        database.save_events_odds_in_json(
                            events, odds, args.bookmaker, args.json)
                    sp.hide()
                    msg = f' {country} - {league}'
                    info = (f'{len(events)} events / {len(odds)} odds  '
                            f'{(time.time() - start_time):5.4}s '
                            f'[{1+i}/{len(competitions)}]')\
                        .rjust(79 - len(msg))
                    print(HTML(f'<seagreen>✔</seagreen>' + msg + info))
                except IndexError as e:
                    sp.hide()
                    msg = f' {country} - {league} [{type(e).__name__}]'
                    count = f'[0/{len(competitions)}]'.rjust(79 - len(msg))
                    print(HTML(f'<red>✘</red>' + msg + count))
                sp.show()
    finally:
        spider.quit()
        del spider


def main():
    args = parse_args()
    competitions = get_competitions(args.bookmaker)
    time.sleep(args.delay * 60)
    if args.schedule == -1:
        job(args, competitions)
    else:
        schedule.every(args.schedule).minutes.do(
            job, args=args, competitions=competitions)
        while True:
            schedule.run_pending()
            delta_next = datetime.timedelta(
                seconds=int(schedule.idle_seconds()))
            sys.stdout.write(f'\rnext job in {str(delta_next)}')
            sys.stdout.flush()
            time.sleep(1)


if __name__ == '__main__':
    main()
