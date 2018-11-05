from dateutil import rrule, parser
import datetime


def utcnow():
    return datetime.datetime.utcnow()


def now():
    return datetime.datetime.now()


def date_range(start, end):
    """
    生成一段日期
    """
    return list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(start), until=parser.parse(end)))


def ago(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0, date=None):
    if date is None:
        dt = now()
    else:
        if isinstance(date, datetime.datetime):
            dt = date
        else:
            dt = parser.parse(date)
    return dt - datetime.timedelta(
        days=days, seconds=seconds, microseconds=microseconds,
        milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)


if __name__ == '__main__':
    print(ago(days=1, date="20181102"))
    print(ago(days=1, date=now()))
