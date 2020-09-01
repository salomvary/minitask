"""Minitask's own version numbers"""

import subprocess

import toml
from django.conf import settings


def _get_version():
    try:
        git_version = subprocess.check_output(
            ["git", "describe", "--always"], encoding="utf-8", stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError:
        git_version = None

    pyproject = toml.load(settings.BASE_DIR / "pyproject.toml")
    toml_version = pyproject["tool"]["poetry"]["version"]

    return toml_version + (f" ({git_version})" if git_version else "")


MINITASK_VERSION = _get_version()
