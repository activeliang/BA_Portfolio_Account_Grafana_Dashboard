#!/bin/bash
export $(cat /app/vars.env | xargs)
/usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1
