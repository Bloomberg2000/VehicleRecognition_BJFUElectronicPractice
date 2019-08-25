import datetime
import hashlib
import json
import math
import enums
from flask import session
from sqlalchemy.ext.declarative import DeclarativeMeta


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                if isinstance(data, datetime.datetime):
                    data = format_time(data)
                try:
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


class PaginationHelper:
    def get_offset(self, pageNum):
        return (pageNum - 1) * self.page_size

    def __init__(self, dataCount, pageSize):
        self.data_count = dataCount
        self.page_size = pageSize
        self.total_page = math.ceil(dataCount / pageSize)
        if self.total_page == 0:
            self.total_page = 1


def queryToJson(query):
    data = json.loads(json.dumps(query, cls=AlchemyEncoder))
    return data


def messageToJson(message="", data=None, queryData=None):
    if data is not None and queryData is None:
        return json.loads(
            json.dumps({
                "message": message,
                "data": json.loads(json.dumps(data))
            })
        )
    if queryData is not None and data is None:
        return json.loads(
            json.dumps({
                "message": message,
                "queryData": queryToJson(queryData)
            })
        )
    if queryData is not None and data is not None:
        return json.loads(
            json.dumps({
                "message": message,
                "data": json.loads(json.dumps(data)),
                "queryData": queryToJson(queryData)
            })
        )
    return json.loads(
        json.dumps({"message": message}))


def md5(text):
    return hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()


#
def calc_price(time):
    money = time * enums.pricePerHour
    return money


def format_time(time):
    return (time).strftime("%Y-%m-%d %H:%M:%S")


def utc_to_local(origin_date_str):
    utc_date = datetime.datetime.strptime(origin_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    local_date = utc_date + datetime.timedelta(hours=8)
    return format_time(local_date)


def current_time():
    return format_time(datetime.datetime.now())


def is_login():
    return True if (session.get('ISLOGIN') == 'true') else False


def who_is_login():
    return session.get('USERUNIQUEID')
