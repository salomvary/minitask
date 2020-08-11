## Development

Requirements:

- Python 3.8
- Poetry

First time setup:

- `poetry install`
- `poetry run python manage.py migrate`

Running the development server:

    poetry run python manage.py runserver

Running migrations:

    poetry run python manage.py migrate

## Running on Ubuntu LTS

    # Extract project to /opt/minitask
    cd /opt/minitask
    apt install python3 python3-pip
    pip3 install -r requirements.txt
    gunicorn minitask.wsgi

The application should be listening at http://hostname:8000.


## Deploying to Heroku

    heroku create my-tasks
    heroku addons:create heroku-postgresql:hobby-dev
    heroku config:set ALLOWED_HOSTS=my-tasks.herokuapp.com
    heroku config:set SERVE_STATIC=true
    heroku config:set ENABLE_HEROKU_LOGGING=true
    heroku config:set DEBUG=false
    # Generate a long secret, eg. with `pwgen -sy 50`
    heroku config:set SECRET_KEY=something_very_secret