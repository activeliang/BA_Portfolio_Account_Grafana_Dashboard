#!/bin/bash
export $(cat /app/db.env | xargs)
/usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1
