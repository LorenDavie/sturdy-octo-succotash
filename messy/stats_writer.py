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
from django.core.cache import cache
from messy.utils import random_hex

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
    key = _get_key()
    return key.generate_url(300)

def write_message(username,city,state,message):
    """ 
    Writes a message.
    """
    from messy.tasks import write_message as wm_job # this is here to avoid a circular import
    
    msg_key = random_hex()
    data = {
        'username':username,
        'city':city,
        'state':state,
        'message':message
    }
    cache.set(msg_key,json.dumps(data),1200)
    wm_job.delay(msg_key) # async message write

def _get_key():
    """ 
    Gets the S3 key.
    """
    conn = boto.connect_s3()
    bucket = conn.create_bucket(settings.MESSY_BUCKET)
    key = Key(bucket)
    key.key = settings.MESSY_KEY
    return key
