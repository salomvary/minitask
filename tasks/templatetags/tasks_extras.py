from urllib.parse import urlencode

from django import template
from minitask.version import MINITASK_VERSION

from ..formats import full_name_format

register = template.Library()

TASK_STATUS_MAP = {
    "open": "primary",
    "in_progress": "warning",
    "done": "success",
}

TASK_PRIORITY_MAP = {
    -2: "success",
    -1: "success",
    0: "secondary",
    1: "danger",
    2: "danger",
}


@register.inclusion_tag("task_status_badge.html")
def task_status_badge(task):
    return {
        "status": task.get_status_display(),
        "class_name": TASK_STATUS_MAP.get(task.status, "secondary"),
    }


@register.inclusion_tag("task_priority_badge.html")
def task_priority_badge(task):
    return {
        "priority": task.get_priority_display(),
        "class_name": TASK_PRIORITY_MAP.get(task.priority, "secondary"),
    }


@register.filter(name="user_str")
def user_str(user):
    """User's full or partial name if available, username otherwise"""

    if user:
        if user.last_name or user.first_name:
            return full_name_format(user.first_name, user.last_name)
        else:
            return user.username
    else:
        return user


@register.filter(name="to_query_str")
def to_query_str(mapping):
    """Turn a mapping into a query string"""

    if mapping:
        query_str = urlencode(mapping)
        if len(query_str) > 0:
            return "?" + query_str

    return ""


@register.simple_tag
def minitask_version():
    return MINITASK_VERSION
