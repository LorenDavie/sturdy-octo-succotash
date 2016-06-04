""" 
Celery tasks for Messy.
"""
from messy.celery import app
from messy.models import Message
from messy.stats_writer import write_stats, write_error
import logging

log = logging.getLogger('messy')

@app.task
def update_stats():
    """ 
    Periodic task to update the stats.
    """
    try:
        city_total = Message.objects.all().values('city').distinct('city').count()
        user_total = Message.objects.all().values('username').distinct('username').count()
        write_stats(city_total,user_total)
    except Exception as e:
        log.exception('Error while rebuilding stats.')
        write_error(e)

