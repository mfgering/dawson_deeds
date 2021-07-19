from bs4 import BeautifulSoup
import requests

class Apt(object):
	def __init__(self, account, unit, owner):
		self.account = account
		self.unit = unit
		self.owner = owner
		self.deed_page = None

	def get_deed_page(self):
		if self.deed_page is None:
			url = f"http://services.wakegov.com/realestate/Account.asp?id={self.account}"
			self.deed_page = BeautifulSoup.get(url)
		return self.deed_page

class Controller(object):
	def __init__(self):
		self.apts = []
		pass

	def search_apts(self):
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
				owner = cols[8].text
				self.apts.append(Apt(account, unit, owner))
				apt_count += 1
			if apt_count == 0:
				break
			page_num += 1
		print(f"Found {len(self.apts)}")
		return self.apts

def main():
	ctlr = Controller()
	ctlr.search_apts()

	print("Done")


if __name__ == '__main__':
	main()