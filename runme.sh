#!/usr/bin/bash
git pull
python3 dawson_deeds.py
git add reports
git commit -m 'cron' 
git push
