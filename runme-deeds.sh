#!/usr/bin/bash
activate() {
  . .venv/bin/activate
  python3 -V
}

git pull
activate
python3 dawson_deeds.py
python3 cypress_deeds.py
git add reports
git commit -m 'cron' 
git push
