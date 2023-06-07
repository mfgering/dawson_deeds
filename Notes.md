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
