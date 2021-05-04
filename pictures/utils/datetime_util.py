import datetime
from json import JSONEncoder


class DatetimeEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()