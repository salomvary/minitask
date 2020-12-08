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

![Screenshot of Minitask in English](screenshot-en.png)

![Screenshot of Minitask in Hungarian](screenshot-hu.png)

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

### Configuration

Minitask can be configured using the following environment variables:

- `SECRET_KEY`: required, a random string. [Django documentation](https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-SECRET_KEY)
- `DEBUG`: optional, defaults to `false`.
- `ENABLE_HEROKU_LOGGING`: optional, defaults to `false`. Set this to `true` when deploying to Heroku.
- `DEBUG_SQL`: optional, defaults to `false`. Set this to true in development to have all SQL queries logged.
- `ALLOWED_HOSTS`: required in production. [Django documentation](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts).
- `DATABASE_URL`: optional, sets up the database connection. Falls back to using [SQLite](https://sqlite.org/index.html)if not provided. [URL Schema documentation](https://github.com/jacobian/dj-database-url#url-schema).
- `LANGUAGE_CODE`: optional, defaults to `en-us`. Sets the user interface language. [Django documentation](https://docs.djangoproject.com/en/3.1/ref/settings/#language-code)
- `TIME_ZONE`: optional, defaults to `UTC`. Set this to your local time zone, eg. `Europe/Budapest`. [Django documentation](https://docs.djangoproject.com/en/3.1/ref/settings/#time-zone)
- `SERVE_STATIC`: optional, defaults to `false` in production. Set this to `true` in production unless you want to take care of serving static files outside of the Django application.
- `REQUIRE_DUE_DATE`: optional, defaults to `false`. When set to `true` makes the due date field of tasks mandatory.
- `REQUIRE_ASSIGNEE`: optional, defaults to `false`. When set to `true` makes the assignee field of tasks mandatory. Enabling this setting also makes the current user the default assignee.

### What database should I use?

Minitask supports [all databases that Django supports](https://docs.djangoproject.com/en/3.1/ref/databases/).

If you don't configure a database, Minitask will use a local SQLite database. SQLite works perfectly for development and might also be acceptable in production, if you run the application on a **single server instance** and the amount of concurrent write operations is very low. More about this [here](https://www.sqlite.org/whentouse.html). The most important warning to keep in mind is that if you happen to outgrow SQLite, migrating to another database engine might be a non-trivial process, as [some people on the internet claim](https://github.com/twoscoops/two-scoops-of-django-1.11/issues/17#issuecomment-295835067).

### Running on Ubuntu LTS

⚠️ This section is heavily work-in-progress.

Don't forget to generate a long secret, eg. with `pwgen -sy 50` or your favorite password manager
and set it with `SECRET_KEY=v3rys3cret` as seen below.


    # Extract project to /opt/minitask
    cd /opt/minitask
    apt install python3 python3-pip
    pip3 install -r requirements.txt
    # Re-run this every time you install a new Minitask version
    SECRET_KEY=v3rys3cret SERVE_STATIC=true DEBUG=false python manage.py collectstatic
    # Replace my.host.name with whatever domain name or ip address you use for accessing the application.
    # You can add more configuration options hire, like LANGUAGE_CODE=hu-hu
    SERVE_STATIC=true ALLOWED_HOSTS=my.host.name DEBUG=false SECRET_KEY=v3rys3cret gunicorn --bind 0.0.0.0:8000 minitask.wsgi
    SECRET_KEY=v3rys3cret python manage.py createsuperuser

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
