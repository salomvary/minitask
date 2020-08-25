from django.utils.formats import get_format


def full_name_format(first_name, last_name):
    full_name = get_format("FULL_NAME")
    return full_name.format(first_name=first_name, last_name=last_name).strip()
