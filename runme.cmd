set DIR="%~dp0"
git pull
python ./dawson_deeds.py
call make-sheet.cmd
cd %DIR%
git add reports
git commit -m "updates"
git push

