@echo off
cd reports
"\Program Files\LibreOffice\program\soffice.exe" --headless -convert-to ods --infilter="CSV:44,34,11,1,1/2/2/2/3/1/4/3/5/1/6/1" dawson.csv
cd
