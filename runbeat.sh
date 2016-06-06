#!/usr/bin/env bash

export DJANGO_SETTINGS_MODULE='messy.settings'

./local.sh celery -A messy beat
