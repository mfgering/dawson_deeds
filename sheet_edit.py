import csv
import socket  # only needed on win32-OOo3.0.0
import uno
import datetime
from com.sun.star.beans import PropertyValue

def do_sheet(model):
	global smgr, svc_dispatch
	try:
		calc_fns = smgr.createInstance("com.sun.star.sheet.FunctionAccess")
		if not model.Sheets.hasByName("dawson_deeds"):
			idx = model.Sheets.getCount()
			model.Sheets.insertNewByName("dawson_deeds", idx)
		sheet = model.getSheets().getByName("dawson_deeds")
		sheet.clearContents(0xffffff)
		#thiscomponent.currentController.setActiveSheet(oNewSheet)
		model.CurrentController.setActiveSheet(sheet)
		with open("reports/dawson.csv") as csv_file:
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

def do_remote():
	global smgr, svc_dispatch

	# get the uno component context from the PyUNO runtime
	localContext = uno.getComponentContext()

	# create the UnoUrlResolver
	resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext )

	# connect to the running office
	ctx = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
	smgr = ctx.ServiceManager

	# get the central desktop object
	desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)

	# access the current writer document
	model = desktop.getCurrentComponent()

	svc_dispatch = smgr.createInstance("com.sun.star.frame.DispatchHelper")

	do_sheet(model)

def foo(self):
	# access the active sheet
	active_sheet = model.CurrentController.ActiveSheet

	# access cell C4
	cell1 = active_sheet.getCellRangeByName("C4")

	# set text inside
	cell1.String = "Hello world"

	# other example with a value
	cell2 = active_sheet.getCellRangeByName("E6")
	cell2.Value = cell2.Value + 1

def do_local():
	global smgr, svc_dispatch, model
	print("Doing local")
	ctx = uno.getComponentContext()
	smgr = ctx.ServiceManager
	desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
	model = desktop.getCurrentComponent()
	svc_dispatch = smgr.createInstance("com.sun.star.frame.DispatchHelper")
	do_sheet(model)

if __name__ == '__main__':
	do_remote()
	print("Done")
else:
	print(f"Local: {__name__}")
	do_local()
