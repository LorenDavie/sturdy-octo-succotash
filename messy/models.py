""" 
Models for Messy.
"""
from django.db import models

class Message(models.Model):
    """ 
    A message, received by the system.
    """
    state = models.CharField('state', max_length=64)
    city = models.CharField('city', max_length=64)
    username = models.CharField('user', max_length=64)
    message = models.TextField('message')
    create_time = models.DateTimeField('date', auto_now_add=True)
    
    class Meta:
        ordering = ['state','city','create_time']

