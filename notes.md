
To create an openoffice spreadsheet from the csv file:

```
"\Program Files\LibreOffice\program\soffice.exe" -convert-to ods --infilter="CSV:44,34,11,1,1/2/2/2/3/1/4/3/5/1/6/1" dawson_deeds.csv
```

Calc Date cells:
[python macro vs calc date](https://ask.libreoffice.org/t/python-macro-vs-calc-date-field/65187)

note that you also may use Calc functions to calculate required values, using com.sun.star.sheet.FunctionAccess service
that way, you create an instance of the service, and then use its callFunction to call e.g. DATEVALUE on the ISO date string

