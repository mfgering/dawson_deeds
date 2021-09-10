$lo = Start-Process -FilePath "C:\Program Files\LibreOffice\program\soffice.exe" -PassThru -ArgumentList '--calc', '--accept="socket,host=localhost,port=2002;urp;" reports\dawson.ods"'
Start-Sleep -Seconds 8
$p = Start-Process -FilePath "C:\Program Files\LibreOffice\program\python.exe" -PassThru -ArgumentList 'sheet_edit.py'
$lo.WaitForExit()
$p.WaitForExit()