The dawson_deeds module will make the csv file. Creating/updating the spreadsheet is done 
via a libreoffice macro.

# Debugging Macros

On Linux, libreoffice uses the system python. The vscode IDE uses the ptvsd python module (use pip).

Inject ptvsd into the python macro:
```python
def my_macro():
    import ptvsd
    ptvsd.enable_attach()
    ptvsd.break_into_debugger()
    print("Should be attachable")

```
In vscode, create a python debug config for remote attach. Launching this config will fail unless the above ptvsd.enable_attach() snippet has been executed first.

----

The python version for the spreadsheet must match LibreOffice (currently 3.8).

The dawson_deeds.fix_python() function updates the python execution environment to 
allow it to communicate with LO to update the spreadsheet. The uno module is specific
to LO.

To create an openoffice spreadsheet from the csv file:

```
"\Program Files\LibreOffice\program\soffice.exe" -convert-to ods --infilter="CSV:44,34,11,1,1/2/2/2/3/1/4/3/5/1/6/1" dawson_deeds.csv
```

Calc Date cells:
[python macro vs calc date](https://ask.libreoffice.org/t/python-macro-vs-calc-date-field/65187)

note that you also may use Calc functions to calculate required values, using com.sun.star.sheet.FunctionAccess service
that way, you create an instance of the service, and then use its callFunction to call e.g. DATEVALUE on the ISO date string


Launching server on Linux:

/usr/bin/soffice --calc --accept="socket,host=localhost,port=2002;urp;" reports/dawson.ods

##Info##

https://wiki.openoffice.org/wiki/Python

https://wiki.documentfoundation.org/Macros/Python_Design_Guide#From_an_IDE_via_LibreOffice_Python_interpreter


# Debugging Libreoffice Python 

Use remote python debugging to port 5678

Install ptvsd package and import it in the script

```
def init_debug(arg1=None):
    import ptvsd
    ptvsd.enable_attach()
    ptvsd.break_into_debugger()
    print("Initialized")

def update_deeds_sheet(arg1=None):
    #Note: when launched from push button, arg1 is com.sun.star.awt.ActionEvent
    import ptvsd
    #ptvsd.wait_for_attach()
    ptvsd.break_into_debugger()
    print("Should be attachable")
```
