from datetime import datetime, date

def purify_date(datestr: date | datetime | str) -> date | None:
    date_obj = None
    if datestr is None:
        pass
    elif isinstance(datestr, (date, datetime)):
        date_obj = datestr
    elif isinstance(datestr, str):
        try:
            date_obj = datetime.strptime(datestr, "%Y/%m/%d")
        except Exception as ex:
            try:
                date_obj = datetime.strptime(datestr, "%y-%m-%d")
            except:
                date_obj = None
    return date_obj

