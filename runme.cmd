set DIR="%~dp0"
git pull
call .venv\scripts\activate.bat
python -V
python ./dawson_deeds.py
::call make-sheet.cmd
cd %DIR%
git add reports
git commit -m "updates"
git push

