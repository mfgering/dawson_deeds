# coding: utf-8
from __future__ import unicode_literals

import uno

def Foo():
    print("Foo")

# Only the specified function will show in the Tools > Macro > Organize Macro dialog:
g_exportedScripts = (Foo,)

if __name__ == "__main__":
    import utils.IDE_Utils as ide
    task = { '/usr/bin/soffice': ['--accept="pipe,name=uno-dawson;urp;"']}
    x =ide.Runner(soffice=task)
    with x:  # Start, Stop
        XSCRIPTCONTEXT = ide.XSCRIPTCONTEXT  # Connect, Adapt
        #x._start()
        Foo()  # Run
