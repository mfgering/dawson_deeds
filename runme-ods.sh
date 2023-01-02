#!/usr/bin/bash
activate() {
  . .venv/bin/activate
  python -V
}

git pull
activate
python3 sheet_edit.py
git add reports
git commit -m 'ods' 
git push
