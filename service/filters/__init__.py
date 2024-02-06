"""
Custom Jinja2 filters will be written here.
""" 
from datetime import date


def dateformat_filter(value, format: str = '%d.%m.%Y'):
    dt_object = date.fromtimestamp(value)
    return dt_object.strftime(format)


def or_blank(value: str|None):
    return value if value is not None else ''


def load_custom_filters(app):
    app.jinja_env.filters['dateformat'] = dateformat_filter
    app.jinja_env.filters['or_blank'] = or_blank
