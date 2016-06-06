""" 
Celery tasks for Messy.
"""
from __future__ import absolute_import
from celery import shared_task

from messy.models import Message
from messy.stats_writer import write_stats, write_error
import logging

log = logging.getLogger('messy')

@shared_task
def update_stats():
    """ 
    Periodic task to update the stats.
    """
    print 'running update stats task'
    try:
        city_total = Message.objects.all().values('city').order_by('city').distinct('city').count()
        user_total = Message.objects.all().values('username').order_by('username').distinct('username').count()
        write_stats(city_total,user_total)
    except Exception as e:
        log.exception('Error while rebuilding stats.')
        write_error(e)

