#!/usr/bin/bash
activate() {
  . .venv/bin/activate
  python -V
}

git pull
activate
python3 dawson_deeds.py
git add reports
git commit -m 'cron' 
git push
