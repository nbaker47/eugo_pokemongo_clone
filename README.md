# ECM2434 Group 28 - EUGO
## Public Address
The EUGO website is public and accessible on [here](https://eugo-344915.ew.r.appspot.com/eugo/login/ "EUGO Login"). The website should contain the current up to date EUGO program.

## Requirements
* \>= python3.9
* pip
* python Packages (look bellow for installation):
  * qrtools
  * requests
  * regex
  * channels

## Setup
In order to be able to run the server, all of the dependencies will have to be installed, this can be done with the command:
```
pip install -r requirements.txt
```
The database should be set-up already(note it is sqlite3), but just in case it isn't, the following commands should be run (within this folder):
```
python manage.py makemigrations
python manage.py migrate
```
If there are still errors with the database, you can try the command:
```
python manage.py migrate --run-syncdb
```
After this is done, all of the setup for the backend should be complete

## Server Start up
In order to be able to access the website, the server should be setup, this can be done with the command:
```
python manage.py runserver
```
The server will then startup after a little bit of time and it will be accessible through [http://localhost:8000]. There are also other options
for running the server, if you would like to have a look at them use the command:
```
python manage.py runserver --help
```

## Tests
To run tests use the command:
```
py manage.py test
```
If it says "OK" at the end then all of the tests ran without errors, otherwise it will tell you which tests failed.
