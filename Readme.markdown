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

