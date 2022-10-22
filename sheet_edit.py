import os
from sys import platform
import random
import subprocess
import time
import csv
import socket  # only needed on win32-OOo3.0.0
import datetime
#NOTE: This module only works with the python version used by LibreOffice
#      The uno module is specific to LibreOffice, not the one from pypy
import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.connection import NoConnectException
from com.sun.star.uno import Exception as UnoException

class Sheet_Editor(object):
    def __init__(self) -> None:
        self.model = None
        self.smgr = None
        self.svc_dispatch = None
        self.curr_dir = os.getcwd()
        self.context = None

    def do_remote(self):
        global smgr, svc_dispatch, model

        # get the uno component context from the PyUNO runtime
        localContext = uno.getComponentContext()
        if localContext is None:
            pass

        ctx = self.context
        #smgr = ctx.ServiceManager
        smgr = self.smgr

        model = None
        while model is None:
            desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
            if desktop is None:
                continue
            model = desktop.getCurrentComponent()

        # get the central desktop object
        desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
        # access the current writer document
        model = desktop.getCurrentComponent()
        svc_dispatch = smgr.createInstance("com.sun.star.frame.DispatchHelper")
        self.do_sheet()
        desktop.terminate()

    def do_sheet(self):
        pass

    def launch_LO(self):
        try:
        # soffice script used on *ix, Mac; soffice.exe used on Win
            if "UNO_PATH" in os.environ:
                sOffice = os.environ["UNO_PATH"]
            else:
                sOffice = "" # lets hope for the best
            sOffice = os.path.join(sOffice, "soffice")
            if platform.startswith("win"):
                sOffice += ".exe"

            # Generate a random pipe name.
            random.seed()
            sPipeName = "uno" + str(random.random())[2:]

            #sOffice2 = 'C:/Program Files/LibreOffice/program/soffice.exe'
            # Start the office process, don't check for exit status since an exception is caught anyway if the office terminates unexpectedly.
            #cmdArray = (sOffice2, "--nologo", "--nodefault", "".join(["--accept=pipe,name=", sPipeName, ";urp;"]))
            cmdArray = (sOffice, "".join(["--accept=pipe,name=", sPipeName, ";urp;"]),
                        '--norestore', self.curr_dir+'/reports/dawson.ods')
            os.chdir('/')
            p = subprocess.Popen(cmdArray)
            os.chdir(self.curr_dir) # change back to original
            #TODO: Is xLocalContext.ServiceManager the same as 
            xLocalContext = uno.getComponentContext()
            resolver = xLocalContext.ServiceManager.createInstanceWithContext(
                "com.sun.star.bridge.UnoUrlResolver", xLocalContext)
            sConnect = "".join(["uno:pipe,name=", sPipeName, ";urp;StarOffice.ComponentContext"])

            # Wait until an office is started, but loop only nLoop times (can we do this better???)
            nLoop = 20
            while True:
                try:
                    xContext = resolver.resolve(sConnect)
                    break
                except NoConnectException:
                    nLoop -= 1
                    if nLoop <= 0:
                        raise Exception("Cannot connect to soffice server.", None)
                    time.sleep(0.5)  # Sleep 1/2 second.

        except Exception as e:  # Any other exception
            raise 
        self.context = xContext
        self.smgr = self.context.ServiceManager

def do_sheet():
    global smgr, svc_dispatch, model, curr_dir
    try:
        calc_fns = smgr.createInstance("com.sun.star.sheet.FunctionAccess")
        if not model.Sheets.hasByName("dawson_deeds"):
            idx = model.Sheets.getCount()
            model.Sheets.insertNewByName("dawson_deeds", idx)
        sheet = model.getSheets().getByName("dawson_deeds")
        sheet.clearContents(0xffffff)
        #thiscomponent.currentController.setActiveSheet(oNewSheet)
        model.CurrentController.setActiveSheet(sheet)
        #TODO: FIX THIS to find the csv file from model.getLocation() url
        with open(f"{curr_dir}/reports/dawson.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            row = 0
            for row_v in csv_reader:
                print(row)
                for col in range(0, len(row_v)):
                    cell = sheet.getCellByPosition(col, row)
                    col_val = row_v[col]
                    try:
                        if col == 3:
                            cell.String = col_val
                            if row > 0:
                                col_val = calc_fns.callFunction("DATEVALUE", [col_val])
                                do_date_fmt(cell)
                                cell.Value = col_val
                        #TODO: Make the URL col a link
                        elif col == 7:
                            cell.String = col_val
                            if row > 0:
                                do_hyperlink_fmt(cell, col_val)
                        else:
                            cell.String = col_val
                    except Exception as exc:
                        pass
                row += 1
        do_autofilter(smgr, sheet)
        ctlr = model.getCurrentController()
        frame = ctlr.getFrame()
        svc_dispatch.executeDispatch(frame, ".uno:Save", "", 0, [])
        print("Have sheet")
    except Exception as exc:
        raise exc
        pass

def do_date_fmt(cell):
    global model, svc_dispatch
    ctlr = model.getCurrentController()
    ctlr.select(cell)
    frame = ctlr.getFrame()
    d = {"Name": "NumberFormatValue", "Value": 37}
    prop = PropertyValue(Name="NumberFormatValue", Value=37)
    svc_dispatch.executeDispatch(frame, ".uno:NumberFormatValue", "", 0, [prop])
 
def do_hyperlink_fmt(cell, url):
    global model, svc_dispatch
    ctlr = model.getCurrentController()
    ctlr.select(cell)
    frame = ctlr.getFrame()
    props = [PropertyValue(Name="Hyperlink.Text", Value=url),
                PropertyValue(Name="Hyperlink.URL", Value=url),
                PropertyValue(Name="Hyperlink.Target", Value=""),
                PropertyValue(Name="Hyperlink.Name", Value=""),
                PropertyValue(Name="Hyperlink.Type", Value=1),
            ]
    svc_dispatch.executeDispatch(frame, ".uno:SetHyperlink", "", 0, props)

def do_autofilter(smgr, sheet):
    global model
    svc = smgr.createInstance("com.sun.star.frame.DispatchHelper")
    cell = sheet.getCellRangeByName("A1:H1")
    ctlr = model.getCurrentController()
    ctlr.select(cell)
    frame = ctlr.getFrame()
    svc.executeDispatch(frame, ".uno:DataFilterHideAutoFilter", "", 0, [])
    svc.executeDispatch(frame, ".uno:DataFilterAutoFilter", "", 0, [])

def do_remote(context = None):
    global smgr, svc_dispatch, model

    # get the uno component context from the PyUNO runtime
    localContext = uno.getComponentContext()

    # create the UnoUrlResolver
    resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext )

    # connect to the running office
    #ctx = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
    if context is None:
        ctx = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
    else:
        ctx = context
    smgr = ctx.ServiceManager

    model = None
    while model is None:
        desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
        if desktop is None:
            continue
        model = desktop.getCurrentComponent()

    # get the central desktop object
    desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
    # access the current writer document
    model = desktop.getCurrentComponent()
    svc_dispatch = smgr.createInstance("com.sun.star.frame.DispatchHelper")
    do_sheet()
    desktop.terminate()

def launch_LO():
    global curr_dir
    try:
       # soffice script used on *ix, Mac; soffice.exe used on Win
        if "UNO_PATH" in os.environ:
            sOffice = os.environ["UNO_PATH"]
        else:
            sOffice = "" # lets hope for the best
        sOffice = os.path.join(sOffice, "soffice")
        if platform.startswith("win"):
            sOffice += ".exe"

        # Generate a random pipe name.
        random.seed()
        sPipeName = "uno" + str(random.random())[2:]

        #MFG Added
        curr_dir = os.getcwd()
        #sOffice2 = 'C:\\\\"Program Files\\"\\LibreOffice\\program\\soffice.exe'
        sOffice2 = 'C:/Program Files/LibreOffice/program/soffice.exe'
        # Start the office process, don't check for exit status since an exception is caught anyway if the office terminates unexpectedly.
        #cmdArray = (sOffice2, "--nologo", "--nodefault", "".join(["--accept=pipe,name=", sPipeName, ";urp;"]))
        cmdArray = (sOffice2, "".join(["--accept=pipe,name=", sPipeName, ";urp;"]),
                    '--norestore', curr_dir+'/reports/dawson.ods')
        #os.spawnv(os.P_NOWAIT, sOffice2, cmdArray)
        os.chdir('/')
        p = subprocess.Popen(cmdArray)
        # ---------

        xLocalContext = uno.getComponentContext()
        resolver = xLocalContext.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", xLocalContext)
        sConnect = "".join(["uno:pipe,name=", sPipeName, ";urp;StarOffice.ComponentContext"])

        # Wait until an office is started, but loop only nLoop times (can we do this better???)
        nLoop = 20
        while True:
            try:
                xContext = resolver.resolve(sConnect)
                break
            except NoConnectException:
                nLoop -= 1
                if nLoop <= 0:
                    raise Exception("Cannot connect to soffice server.", None)
                time.sleep(0.5)  # Sleep 1/2 second.

    except Exception as e:  # Any other exception
        raise 
    return xContext

if __name__ == '__main__':
    ctlr = Sheet_Editor()
    ctlr.launch_LO()
    ctlr.do_remote()
    print("Done")
else:
    print(f"Local: {__name__}")
