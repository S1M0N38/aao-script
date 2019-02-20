import json
import os

import psycopg2
from psycopg2 import sql

# TODO update events


def save_events_odds_in_json(events, odds, bookmaker, path):
    country, league = events[0]['country'], events[0]['league']
    events_file = f'events_{bookmaker}_{country}_{league}.json'
    odds_file = f'odds_{bookmaker}_{country}_{league}.json'
    with open(os.path.join(path, events_file), 'w') as f:
        json.dump(events, f, indent=2, default=str)
    with open(os.path.join(path, odds_file), 'w') as f:
        json.dump(odds, f, indent=2, default=str)


def save_results_in_json(events, path):
    results_file = 'results.json'
    with open(os.path.join(path, results_file), 'w') as f:
        json.dump(events, f, indent=2, default=str)


def save_events_odds_in_db(events, odds, bookmaker):
    with DB() as db:
        for event, odd in zip(events, odds):
            event_id = db.search_event(event)
            if event_id is None:
                event_id = db.insert_event(event)
            odd_id = db.search_odd(event_id, bookmaker)
            if odd_id:
                db.delete_odd(odd_id)
            db.insert_odd(event_id, bookmaker, odd, 'api_all_odds')
            db.insert_odd(event_id, bookmaker, odd, 'api_active_odds')
        db.connection.commit()


def update_events_in_db(events):
    with DB() as db:
        for event in events:
            db.update_event(event)
        db.connection.commit()


class DB:

    def __init__(self):
        self.dbname = 'aao'
        self.user = os.environ['DB_USER']
        self.password = os.environ['DB_PASSWORD']
        self.host = os.environ['DB_HOST']
        self.port = int(os.environ['DB_PORT'])

    def __enter__(self):
        self.connection = psycopg2.connect(
            dbname=self.dbname, user=self.user,
            password=self.password, host=self.host, port=self.port)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, *args):
        self.cursor.close()
        self.connection.close()

    def search_event(self, event):
        self.cursor.execute(
            ''' SELECT id FROM api_events WHERE (
            DATE(datetime) = %s AND country = %s AND league = %s AND (
            home_team = %s OR away_team = %s)) LIMIT 1''',
            (event['datetime'].date(), event['country'],
             event['league'], event['home_team'], event['away_team']))
        event_id = self.cursor.fetchone()
        if event_id is None:
            return None
        return event_id[0]

    def search_odd(self, event_id, bookmaker):
        self.cursor.execute(
            ''' SELECT id FROM api_active_odds WHERE(
            bookmaker = %s AND event_id = %s) LIMIT 1''',
            (bookmaker, event_id))
        odd_id = self.cursor.fetchone()
        if odd_id is None:
            return None
        return odd_id[0]

    def delete_odd(self, odd_id):
        self.cursor.execute(
            '''DELETE FROM api_active_odds WHERE id = %s''', (odd_id,))

    def insert_event(self, event):
        self.cursor.execute(
            '''INSERT INTO api_events (datetime, country, league, home_team,
            away_team) VALUES (%s, %s, %s, %s, %s)''',
            (event['datetime'], event['country'], event['league'],
             event['home_team'], event['away_team']))
        self.cursor.execute('SELECT MAX(id) FROM api_events')
        event_id = self.cursor.fetchone()[0]
        return event_id

    def insert_odd(self, event_id, bookmaker, odd, table):
        self.cursor.execute(sql.SQL(
            '''INSERT INTO {} (datetime, bookmaker,
            full_time_result, draw_no_bet, both_teams_to_score,
            double_chance, under_over, event_id)
            VALUES (current_timestamp, %s, %s, %s, %s, %s, %s, %s)''')
            .format(sql.Identifier(table)),
            (bookmaker, json.dumps(odd['full_time_result']),
             json.dumps(odd['draw_no_bet']),
             json.dumps(odd['both_teams_to_score']),
             json.dumps(odd['double_chance']), json.dumps(odd['under_over']),
             event_id))

    def update_event(self, event):
        ...
