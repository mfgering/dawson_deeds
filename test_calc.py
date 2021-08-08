import csv
import socket  # only needed on win32-OOo3.0.0
import uno
import datetime

def do_sheet(model):
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
						if row == 0 or col == 1:
							cell.String = col_val
						else:
							if col == 3:
								col_val = calc_fns.callFunction("DATEVALUE", [col_val])
								do_date_fmt(cell)
							cell.Value = col_val
					except Exception as exc:
						pass
				row += 1
		do_autofilter(smgr, sheet)
		print("Have sheet")
	except Exception as exc:
		raise exc
		pass

def do_date_fmt(cell):
	ctlr = model.getCurrentController()
	ctlr.select(cell)
	frame = ctlr.getFrame()
	svc_dispatch.executeDispatch(frame, ".uno:NumberFormatValue", "", 0, ["NumberFormatValue", 37])
 

def do_autofilter(smgr, sheet):
	svc = smgr.createInstance("com.sun.star.frame.DispatchHelper")
	cell = sheet.getCellRangeByName("A1:F1")
	ctlr = model.getCurrentController()
	ctlr.select(cell)
	frame = ctlr.getFrame()
	svc.executeDispatch(frame, ".uno:DataFilterAutoFilter", "", 0, [])

def call_dispatch(doc, url, args=()):
	frame = doc.getCurrentController().getFrame()
	dispatch = create_instance('com.sun.star.frame.DispatchHelper')
	dispatch.executeDispatch(frame, url, '', 0, args)
	return

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

print("Done")