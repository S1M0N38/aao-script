import json
import os

import psycopg2


def save_in_json(events, odds, bookmaker, path):
    assert events
    assert odds
    country, league = events[0]['country'], events[0]['league']
    events_file = f'events_{bookmaker}_{country}_{league}.json'
    odds_file = f'odds_{bookmaker}_{country}_{league}.json'
    with open(os.path.join(path, events_file), 'w') as f:
        json.dump(events, f, indent=2, default=str)
    with open(os.path.join(path, odds_file), 'w') as f:
        json.dump(odds, f, indent=2, default=str)


def save_in_db(events, odds, bookmaker):
    DB_USER = os.environ['DB_USER']
    DB_PASSWORD = os.environ['DB_PASSWORD']
    DB_HOST = os.environ['DB_HOST']
    DB_PORT = os.environ['DB_PORT']

    def search_event(event):
        cur.execute('''SELECT event_id FROM events WHERE (
                    DATE(time) = %s AND
                    country LIKE %s AND
                    league LIKE %s AND (
                    home_team %% %s OR
                    away_team %% %s))
                    LIMIT 1''',
                    (event['datetime'].date(), event['country'],
                     event['league'], event['home_team'], event['away_team']))
        event_id = cur.fetchone()
        # print(event_id)
        if event_id is None:
            return None
        return event_id[0]

    def insert_event(event):
        cur.execute('''INSERT INTO events
                    (time, country, league, home_team, away_team)
                    VALUES (%s, %s, %s, %s, %s)''',
                    (event['datetime'], event['country'], event['league'],
                     event['home_team'], event['away_team']))
        cur.execute('SELECT MAX(event_id) FROM events')
        event_id = cur.fetchone()[0]
        return event_id

    def insert_odd(event_id, bookmaker, odd):
        assert bookmaker in ('bet365', '888sport', 'bwin', 'williamhill')

        def dict2json(key):
            if key in odd:
                return json.dumps(odd[key])
            return None
        full_time_result = dict2json('full_time_result')
        draw_no_bet = dict2json('draw_no_bet')
        both_teams_to_score = dict2json('both_teams_to_score')
        double_chance = dict2json('double_chance')
        under_over = dict2json('under_over')
        cur.execute('''INSERT INTO odds
                    (event_id, time, bookmaker, full_time_result, draw_no_bet,
                     both_teams_to_score, double_chance, under_over)
                    VALUES (%s, current_timestamp, %s, %s, %s, %s, %s, %s)''',
                    (event_id, bookmaker, full_time_result, draw_no_bet,
                     both_teams_to_score, double_chance, under_over))

    conn = psycopg2.connect(
        dbname='aao', user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=int(DB_PORT)
    )
    cur = conn.cursor()
    for event, odd in zip(events, odds):
        event_id = search_event(event)
        if event_id is None:
            event_id = insert_event(event)
        insert_odd(event_id, bookmaker, odd)
    conn.commit()
    cur.close()
    conn.close()
