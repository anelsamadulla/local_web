from datetime import date


def dateformat_filter(value, format: str = '%d.%m.%Y'):
    dt_object = date.fromtimestamp(value)
    return dt_object.strftime(format)


def load_custom_filters(app):
    app.jinja_env.filters['dateformat'] = dateformat_filter
