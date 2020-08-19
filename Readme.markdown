# Minitask

Minitask is rather simple project management application for the web.
It is not much more than a multi-user to-do list. It does not try to be
beautiful, it tries to be simple both on terms of underlying technology
and user experience.

If you need 0.5% of Jira's functionality, Minitask is a great alternative.

Minitask is currently only available for self-hosting, which means you have
to deploy it to your own infrastructure or to the cloud. If you are interested
in paying for a hosted version,
[get in touch](mailto:marton@salomvary.com?subject=Minitask%20hosting).

The user interface is not only available in English but also Hungarian.
Other languages can easily be added. If you are interested in translating
Minitask into your language,
[let me know](mailto:marton@salomvary.com?subject=Minitask%20translation)!

## Project status

As of August 2020 the project is under active development and is **not yet
considered to be stable**.

## Screenshots

![Screenshot of Minitask](screenshot.png)

## Demo

- https://minitask.herokuapp.com/
- Username: demo
- Password: Demodemo1

## Development

Minitask is a [Django](https://www.djangoproject.com/) application. If you want to
make changes or fix bugs, follow the instructions below.

Requirements:

- [Python 3.8](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/)

First time setup:

    poetry install
    poetry run python manage.py migrate

Running the development server:

    poetry run python manage.py runserver
    # To enable SQL logging:
    DEBUG_SQL=true poetry run python manage.py runserver

Specifying the server language:

    LANGUAGE_CODE=hu-hu poetry run python manage.py runserver

Running migrations:

    poetry run python manage.py migrate

Working with translations:

    poetry run django-admin makemessages --locale=hu
    # Edit tasks/locale/hu/LC_MESSAGES/django.po
    poetry run django-admin compilemessages

## Deployment

Django has excellent [documentation on deploying applications to production](https://docs.djangoproject.com/en/3.1/howto/deployment/). Below are a few concrete examples.

### Running on Ubuntu LTS

⚠️ This section is heavily work-in-progress.

    # Extract project to /opt/minitask
    cd /opt/minitask
    apt install python3 python3-pip
    pip3 install -r requirements.txt
    gunicorn minitask.wsgi

The application should be listening at http://hostname:8000.


### Deploying to Heroku

[Heroku](https://www.heroku.com/) is one of the easiest cloud platform to deploy to.
If you are not familiar with Heroku [start here](https://devcenter.heroku.com/articles/getting-started-with-python). Minitask works fine on a free Heroku account.

    heroku create my-tasks
    heroku addons:create heroku-postgresql:hobby-dev
    heroku config:set ALLOWED_HOSTS=my-tasks.herokuapp.com
    heroku config:set SERVE_STATIC=true
    heroku config:set ENABLE_HEROKU_LOGGING=true
    heroku config:set DEBUG=false
    # Generate a long secret, eg. with `pwgen -sy 50`
    heroku config:set SECRET_KEY=something_very_secret
    # Optional
    heroku config:set LANGUAGE_CODE=hu-hu
    heroku config:set TIME_ZONE=Europe/Budapest
    # Deploy
    git push heroku master
    # Create superuser
    heroku run python manage.py createsuperuser

