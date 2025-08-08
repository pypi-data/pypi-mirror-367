# filters.py
from datetime import datetime, date
from .utils import purify_date


def format_date(datestr: str, format: str = '%b %d, %Y') -> str:
    date_obj = purify_date(datestr)
    if date_obj is None:
        return datestr
    return date_obj.strftime(format)


FILTERS = {
    'format_date': format_date
}