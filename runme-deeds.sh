#!/usr/bin/bash
activate() {
  . .venv/bin/activate
  python3 -V
}

git pull
activate
echo "Running dawson_deeds.py"
python3 dawson_deeds.py
echo "Running cypress_deeds.py"
python3 cypress_deeds.py
echo "Commiting changes..."
git add reports
git commit -m 'cron' 
git push
echo "Done"
