""" 
Writes stats (or error condition) to S3, where it can be retrieved en masse.

Note - all the write methods, and _refresh_url is meant to be accessed in a single-threaded manner,
triggered by the messy.tasks.update_stats periodic task. They should not be accessed from an
HTTP request/response cycle.
"""
import boto
from boto.s3.key import Key
import json
from django.conf import settings
from datetime import datetime, timedelta
from messy.models import MessageStatsURL

stats_url = None
url_expires = None

def write_stats(city_total,user_total):
    """ 
    Writes the summary stats into S3.
    """
    data = {
        'result':'success',
        'cities':city_total,
        'users':user_total,
    }
    key = _get_key()
    key.set_contents_from_string(json.dumps(data))

def write_error(error):
    """ 
    Writes the error message into S3.
    """
    data = {
        'result':'error',
        'error':unicode(error),
    }
    key = _get_key()
    key.set_contents_from_string(json.dumps(data))

def get_url():
    """ 
    Gets the URL pointing to the S3 locations where the data is stored. This is the only
    function in this module that may be accessed within an HTTP request/response cycle, 
    e.g. multi-threaded.
    """
    if stats_url and url_expires > datetime.now():
        return stats_url
    else:
        return _get_url()

def _get_url():
    """ 
    Regenerates the URL from the database.
    """
    now = datetime.now()
    thirty_days = timedelta(seconds=60 * 60 * 24 * 30) # 30 day url expiry
    thirty_days_ago = now - thirty_days
    stats_url_model = MessageStatsURL.objects.filter(updated__gte=thirty_days_ago).last()
    if not stats_url_model:
        key = _get_key()
        new_url = key.generate_url(thirty_days.seconds)
        stats_url_model = MessageStatsURL.objects.create(url=new_url)
        MessageStatsURL.objects.exclude(pk=stats_url_model.pk).delete() # clean up old url objects in db
        
    stats_url = stats_url_model.url
    stats_expires = stats_url_model.updated + thirty_days
    return stats_url

def _get_key():
    """ 
    Gets the S3 key.
    """
    conn = boto.connect_s3()
    bucket = conn.create_bucket(settings.MESSY_BUCKET)
    key = Key(bucket)
    key.key = settings.MESSY_KEY
    return key
