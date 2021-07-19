import csv
import datetime
from bs4 import BeautifulSoup
import requests

class Apt(object):
	def __init__(self, account, unit, owner):
		self._deed_page = None
		self._account = account
		self._unit = unit
		self._owner = owner

	@property
	def account(self):
		return self._account

	@property
	def unit(self):
		return self._unit

	@property
	def owner(self):
		return self._owner
	@property
	def account(self):
		return self._account

	@property
	def deed_date(self):
		self._deed_date = self._get_value('Deed Date')
		if self._deed_date != None:
			format_str = '%m/%d/%Y'
			d = datetime.datetime.strptime(self._deed_date, format_str)
			return d
		return None

	@property
	def pkg_sale_price(self):
		self._pkg_sale_price = self._get_value('Pkg Sale Price')
		if self._pkg_sale_price is not None:
			val = 0
			try:
				val = int(''.join([c for c in self._pkg_sale_price if c != ',' and c != '$']))
			except:
				pass
			return val
		return None

	@property
	def heated_area(self):
		self._heated_area = self._get_value('Heated Area')
		result = 0
		try:
			result = int(''.join([c for c in self._heated_area if c != ',']))
		except:
			pass
		return result

	@property
	def assessed(self):
		self._assessed = self._get_value('Total Value Assessed*')
		if self._assessed is not None:
			val = 0
			try:
				val = int(''.join([c for c in self._assessed if c != ',' and c != '$']))
			except:
				pass
			return val
		return None

	def _get_deed_page(self):
		if self._deed_page is None:
			url = f"http://services.wakegov.com/realestate/Account.asp?id={self._account}"
			page = requests.get(url)
			self._deed_page = BeautifulSoup(page.content, 'html.parser')
		return self._deed_page

	def _get_value(self, name):
		page = self._get_deed_page()
		for row in page.find_all('tr'):
			cols = row.find_all('td')
			for col_num in range(0, len(cols)):
				if cols[col_num].text == name:
					p = cols[col_num].parent
					cols2 = p.find_all('td')
					value = cols2[1].text
					return value

class Apts(object):
	def __init__(self):
		self._apts = None

	@property
	def apts(self):
		if self._apts is None:
			self._apts = self.search_apts()
		return self._apts

	def search_apts(self):
		self._apts = []
		# Note: need to iterate through all the pages
		url = 'http://services.wakegov.com/realestate/AddressSearch.asp'
		#params = {'c1': '1857', 'stype': 'addr', 'stnum': '317', 'stname': 'MORGAN', 'locidList': '1857'}
		page_num = 1
		while True:
			url = f'http://services.wakegov.com/realestate/AddressSearch.asp?stnum=317&stype=addr&stname=morgan&locidList=1857&spg={page_num}'
			page = requests.get(url)
			soup = BeautifulSoup(page.content, 'html.parser')
			apt_count = 0
			# search thru all tr looking for good results
			for row in soup.find_all('tr'):
				cols = row.find_all('td')
				if len(cols) < 9 or cols[2].text != '317':
					continue
				account = cols[1].text
				unit = cols[3].text
				owner = cols[9].text
				self._apts.append(Apt(account, unit, owner))
				apt_count += 1
			if apt_count == 0:
				break
			page_num += 1
		print(f"Found {len(self._apts)}")
		return self._apts

	def by_unit_num(self, reverse=False):
		apts = self.apts
		apts.sort(key=lambda x: x.unit, reverse=reverse)
		return apts

	def by_deed_date(self, reverse=False):
		apts = self.apts
		apts.sort(key=lambda x: x.deed_date, reverse=reverse)
		return apts

	def by_heated_area(self, reverse=False):
		apts = self.apts
		apts.sort(key=lambda x: x.heated_area, reverse=reverse)
		return apts

	def get_unit(self, unit_str):
		for apt in self.apts:
			if apt.unit == unit_str:
				return apt
		return None
	
	def make_csv(self, fn):
		with open(fn, "w", newline='') as fp:
			field_names = ['unit_num', 'owner', 'heated_area', 'deed_date', 'pkg_sale_price', 'assessed']
			writer = csv.DictWriter(fp, fieldnames=field_names)
			writer.writeheader()
			for apt in self.apts:
				writer.writerow({'unit_num': apt.unit, 
					'owner': apt.owner, 'heated_area': apt.heated_area, 
					'deed_date': apt.deed_date, 'pkg_sale_price': apt.pkg_sale_price, 
					'assessed': apt.assessed})

def print_apts(apts, fn, title=''):
	with open(fn, 'w') as fp:
		print(f"\n{title}\n\n", file=fp)
		for apt in apts:
			print("-----------------------", file=fp)
			print(f"Unit: {apt.unit}\tOwner: {apt.owner}", file=fp)
			print(f"Heated Area: {apt.heated_area}", file=fp)
			print(f"Deed Date: {apt.deed_date.strftime('%m/%d/%Y')}", file=fp)
			print(f"Pkg Sale Price: {apt.pkg_sale_price}", file=fp)
			print(f"Assessed: {apt.assessed}", file=fp)
		fp.close()

def main():
	ctlr = Apts()
	ctlr.make_csv("./reports/dawson.csv")
	apts = ctlr.by_unit_num()
	print_apts(apts, "./reports/by_unit.txt", "By Unit")
	print_apts(ctlr.by_deed_date(reverse=True), "./reports/by_deed.txt", "By Deed Date")
	print_apts(ctlr.by_heated_area(reverse=True), "./reports/by_heated_area.txt", "By Heated Area")
	print("Done")


if __name__ == '__main__':
	main()