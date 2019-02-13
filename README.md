# aao-script

### Install
first you need to install aao (pip package is not ready yet)
```shell
cd 
git clone https://github.com/S1M0N38/aao.git
```
now install aao-script
```shell
cd
git clone https://github.com/S1M0N38/aao-script.git 
pipenv install
pipenv install $HOME/aao --dev
```
when you need to upgrade aao and aao-script perform a `git pull` in both repos

### Config
create in .env file in */aao-script* for database config (if you want)
```bashrc
export DB_USER="my_user"
export DB_PASSWORD="my_password"
export DB_HOST="localhost"
export DB_PORT="5432"
```
alternatively you can save data in json file with the `--json [path]` flag.
The .env file can be use to store login credentials for spiders, proxy or other things.


### Usage
activate virtualenv `pipenv shell`
run the script `python run.py bwin`

### Docs
get the help `python run.py --help`
