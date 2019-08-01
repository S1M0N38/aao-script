# aao-script

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a57832b88a4e4f5ba0954add05cee976)](https://www.codacy.com/app/S1M0N38/aao-script?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=S1M0N38/aao-script&amp;utm_campaign=Badge_Grade)

A collection of script that use [aao](https://github.com/S1M0N38/aao) to 
collect **events**, **odds**, **results** data about football matches.

## ⬇️ Installation
In order to use aao-script clone this repository 
```shell
git clone https://github.com/S1M0N38/aao-script.git 
```
and the install the required dependencies 
([pipenv](https://pipenv.readthedocs.io/en/latest/) strongly recommended)
```shell
cd aao-script
pipenv install
```
when you need to upgrade aao and aao-script perform a `git pull` and `pipenv install`

## ⚙️ Configuration
**If you plan to use a postgresql database**:
Install `psql` 9.6 (google it and follow the guide for your OS) then
within the psql-command line create a database called *aao* and a 
user named *script* 
```shell
postgres=# CREATE DATABASE aao;
postgres=# CREATE USER script WITH ENCRYPTED PASSWORD 'my_password';
postgres=# GRANT CONNECT ON DATABASE aao TO script;
postgres=# GRANT USAGE ON SCHEMA public TO script;
postgres=# GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO script;
postgres=# GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO script;
postgres=# GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO script;
postgres=# GRANT ALL PRIVILEGES ON DATABASE aao TO script;
postgres=# \q
```
Now you have to load the schema in the new database that you have
create with
```shell
psql -d aao -f db.sql
```
postgresql db should be now setup (you can use a GUI client for 
postgresql in order to access db in a easy way).
Create in .env file in */aao-script* for database configuration 
```bashrc
export DB_USER="script"
export DB_PASSWORD="my_password"
export DB_HOST="localhost"
export DB_PORT="5432"
```
After modify *.env* file you need to restart the virtualenv to
correctly load envs variables.

**Alternatively** you can save data in json file with the `--json [path]` flag.
The .env file can be use to store login credentials for spiders, proxy or other things.

Other configuration files are the *competitions* files. They are *.csv* store in
[competiton/{bookmaker}.csv](https://github.com/S1M0N38/aao-script/tree/master/competitions).
Here you can specify the pain `{country},{league}` scrape by each spider.

## ⚡️ Usage
First got to your local */aao-script* directory.
Then you need to activate the virtualenv with the command `pipenv shell`.

### Get events and odds
With the *scrape.py* script you are able to scrape four of the major betting site (
[888sport](https://www.888sport.com/),
[bet365](https://www.bet365.com/), 
[bwin](https://sports.bwin.com/en/sports#) and 
[williamhill](http://sports.williamhill.com/betting/en-gb))
and get events and odds.
```shell
python scrape.py {spider}
```
**Important** the spiders used by *scrape.py* work only on the english version of
the betting site. Be sure to have access to the english version with no problem.

Betting site sometime have country limitation, you can use the script anyway
proving a proxy (with `--proxy`) or using a VPN. (Note: if you want to scrape *bet365* 
and from your location you cannot access the english version of the site, create a 
english accont and the pass the credential with `--username {user} --password {passwd}`)

### Get result
*results.py* is a really simple script that scrape 
[livescore.cz](https://www.livescore.cz/) 
to get today's football match results.
```shell
python results.py
```
Like `scrape.py` it can save the data in the postgresql database with `--db` flag
but it can also store the colleced date in a json file (`--json {path}`).

## 📖 Documentation
There is no complete documentation for this project;
you can get the information from this README.md file or
using the help flag: `python scrape.py --help` and `python results.py --help`
