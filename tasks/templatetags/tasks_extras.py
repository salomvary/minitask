from django import template

register = template.Library()

TASK_STATUS_MAP = {
    "open": "primary",
    "in_progress": "warning",
    "done": "success",
}


@register.inclusion_tag("task_status_badge.html")
def task_status_badge(task):
    return {
        "status": task.get_status_display(),
        "class_name": TASK_STATUS_MAP.get(task.status, "secondary"),
    }
