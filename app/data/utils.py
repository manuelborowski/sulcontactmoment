import datetime

from sqlalchemy import desc

from app import flask_app, log, data, db
from app.data import settings
from app.data import models as mmodels


def data_done():
    db.session.commit()


def raise_error(message, details=None):
    error = Exception(f'm({message}), d({details}), td({type(details).__name__})')
    raise error


# standardized way to make a key from strings: sort alphabetically and concatenate
def make_key(item_list):
    return make_list(item_list, seperator=',')

def extend_key(item1, item2=None):
    if isinstance(item1, list):
        return ','.join(item1)
    return ','.join([item1, item2])


# standardized way to concatenate strings: sort alphabetically and concatenate; seperated by comma
def make_list(item_list, seperator=', '):
    return seperator.join(sorted(item_list))


def datetime_to_dutch_datetime_string(date):
    return mmodels.datetime_to_dutch_datetime_string(date)