""" 
Celery tasks for Messy.
"""
from __future__ import absolute_import
from celery import shared_task

from messy.models import Message
from messy.stats_writer import write_stats, write_error
from django.core.cache import cache
import json
import logging

log = logging.getLogger('messy')

@shared_task
def update_stats():
    """ 
    Periodic task to update the stats.
    """
    try:
        city_total = Message.objects.all().values('city').order_by('city').distinct('city').count()
        user_total = Message.objects.all().values('username').order_by('username').distinct('username').count()
        write_stats(city_total,user_total)
    except Exception as e:
        log.exception('Error while rebuilding stats.')
        write_error(e)


@shared_task
def write_message(message_key):
    """ 
    Writing the task to the database async.
    """
    try:
        data = json.loads(cache.get(message_key))
        Message.objects.create(state=data['state'],
                               city=data['city'],
                               username=data['username'],
                               message=data['message'])
    except Exception as e:
        log.exception('Error while writing message.')
