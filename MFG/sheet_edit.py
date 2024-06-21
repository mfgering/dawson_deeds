import os
import sys
from sys import platform
import random
import subprocess
import time
import csv
import urllib
import pathlib

#NOTE: ON WINDOWS, This module only works with the python version used by LibreOffice
#      The uno module is specific to LibreOffice, not the one from pypy
import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.connection import NoConnectException
from com.sun.star.uno import Exception as UnoException

class Sheet_Editor(object):
    def __init__(self, csv_filename, ods_filename) -> None:
        self.model = None
        self.smgr = None
        self.svc_dispatch = None
        self.curr_dir = os.getcwd()
        self.context = None
        self.ctlr = None
        self.csv_filename = csv_filename
        self.ods_filename = ods_filename
        self.header_row_num = 4
        self.timestamp_row = 2

    def do_local(self):
        localContext = uno.getComponentContext()
        self.context = localContext
        self.smgr = localContext.ServiceManager
        model = None
        desktop = None
        while model is None:
            desktop = self.smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",self.context)
            if desktop is None:
                continue
            model = desktop.getCurrentComponent()
        self.model = model
        assert(desktop is not None)
        self.ctlr = model.getCurrentController()
        self.frame = self.ctlr.getFrame()
        self.do_sheet(desktop)
        #desktop.terminate()
    
    def do_remote(self):

        # get the uno component context from the PyUNO runtime
        localContext = uno.getComponentContext()
        smgr = self.smgr
        assert(smgr is not None)

        model = None
        desktop = None
        while model is None:
            desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",self.context)
            if desktop is None:
                continue
            model = desktop.getCurrentComponent()
        self.model = model
        assert(desktop is not None)
        self.ctlr = model.getCurrentController()
        self.frame = self.ctlr.getFrame()
        # get the central desktop object
        self.do_sheet(desktop)
        desktop.terminate()

    def do_sheet(self, desktop):
        model = self.model
        assert(self.smgr is not None)
        assert(self.model is not None)
        self.svc_dispatch = self.smgr.createInstance("com.sun.star.frame.DispatchHelper")
        svc_dispatch = self.svc_dispatch
        try:
            calc_fns = self.smgr.createInstance("com.sun.star.sheet.FunctionAccess")
            if not model.Sheets.hasByName("dawson_deeds"):
                idx = model.Sheets.getCount()
                model.Sheets.insertNewByName("dawson_deeds", idx)
            sheet = model.getSheets().getByName("dawson_deeds")
            sheet.clearContents(0xffffff)
            model.CurrentController.setActiveSheet(sheet)
            # Set the timestamp in the sheet
            mtime = os.path.getmtime(self.csv_filename)
            m_str = time.ctime(mtime)
            cell = sheet.getCellByPosition(1, self.timestamp_row)
            cell.String = f"Last modified: {m_str}"
            with open(self.csv_filename) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                row = self.header_row_num
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
                                    self.do_date_fmt(cell)
                                    cell.Value = col_val
                            #TODO: Make the URL col a link
                            elif col == 7:
                                cell.String = col_val
                                if row > 0:
                                    self.do_hyperlink_fmt(cell, col_val)
                            else:
                                cell.String = col_val
                        except Exception as exc:
                            pass
                    row += 1
            self.do_autofilter(sheet)
            svc_dispatch.executeDispatch(self.frame, ".uno:Save", "", 0, [])
            print("Have sheet")
        except Exception as exc:
            raise exc

    def do_autofilter(self, sheet):
        hdr_row_num = self.header_row_num + 1
        cell = sheet.getCellRangeByName(f"A{hdr_row_num}:H{hdr_row_num}")
        self.ctlr.select(cell)
        #self.svc_dispatch.executeDispatch(self.frame, ".uno:DataFilterHideAutoFilter", "", 0, [])
        #self.svc_dispatch.executeDispatch(self.frame, ".uno:DataFilterAutoFilter", "", 0, [])

    def do_date_fmt(self, cell):
        self.ctlr.select(cell)
        d = {"Name": "NumberFormatValue", "Value": 37}
        prop = PropertyValue(Name="NumberFormatValue", Value=37)
        self.svc_dispatch.executeDispatch(self.frame, ".uno:NumberFormatValue", "", 0, [prop])
    
    def do_hyperlink_fmt(self, cell, url):
        self.ctlr.select(cell)
        props = [PropertyValue(Name="Hyperlink.Text", Value=url),
                    PropertyValue(Name="Hyperlink.URL", Value=url),
                    PropertyValue(Name="Hyperlink.Target", Value=""),
                    PropertyValue(Name="Hyperlink.Name", Value=""),
                    PropertyValue(Name="Hyperlink.Type", Value=1),
                ]
        self.svc_dispatch.executeDispatch(self.frame, ".uno:SetHyperlink", "", 0, props)

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

            # Start the office process, don't check for exit status since an exception is caught anyway if the office terminates unexpectedly.
            cmdArray = (sOffice, "".join(["--accept=pipe,name=", sPipeName, ";urp;"]),
                        '--norestore', self.ods_filename)
            os.chdir('/')
            p = subprocess.Popen(cmdArray)
            os.chdir(self.curr_dir) # change back to original
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

def setup_debug(arg1=None):
    import debugpy
    debugpy.listen(('0.0.0.0', 5678))
    print("Waiting for debugger attach...")
    debugpy.wait_for_client()
    print("Debugger attached")
    
def update_deeds_sheet(arg1=None):
    #Note: when launched from push button, arg1 is com.sun.star.awt.ActionEvent
    import debugpy
    debugpy.breakpoint()
    #sys.args are used only with standalone version, not the macro version
    # Use relative file if exists, else check absolute
    rel_file = 'projects/dawson_deeds/reports/dawson.csv'
    csv_filename = rel_file if os.path.isfile(rel_file) else f"/home/mgering/{rel_file}"
    #csv_filename = (len(sys.argv) > 1 and sys.argv[1]) or pathlib.Path(os.getcwd())/'projects/'/'dawson_deeds'/'reports'/'dawson.csv'
    #ods_filename = (len(sys.argv) > 2 and sys.argv[2]) or pathlib.Path(os.getcwd())/'projects/'/'dawson_deeds'/'reports'/'dawson.ods'
    ods_filename = None #TODO: FIX THIS
    ctlr = Sheet_Editor(csv_filename, ods_filename)
    ctlr.do_local()

g_exportedScripts = (setup_debug, update_deeds_sheet)