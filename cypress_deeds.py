import csv
import datetime
from bs4 import BeautifulSoup
import requests
import logging
import os
import sys
import operator

addr_cottage_map = {
    '8709': 'laurel',
    '8731': 'laurel?',
    '8728': 'laurel?',
    '8739': 'laurel?',
    '8722': 'laurel?'}

class Apt(object):
    def __init__(self, account, unit, st_num=None, st_name=None):
        self._deed_page = None
        self._owner = None
        self._account = account
        self._unit = unit
        self._deed_url = f"http://services.wakegov.com/realestate/Account.asp?id={self._account}"
        self.st_num = st_num
        self.st_name = st_name

    @property
    def unit(self):
        return self._unit

    @property
    def model(self):
        if self.style == 'cottage':
            if self.st_num in addr_cottage_map:
                return addr_cottage_map[self.st_num]
        return ''
    
    @property
    def style(self):
        if self._pkg_sale_price == '':
            return 'admin'
        if (self._unit is None or len(self._unit) == 0):
            return 'cottage'
        else:
            try:
                int(self._unit)
            except:
                return 'admin'
            return 'villa'
        
    @property
    def owner(self):
        if self._owner is None:
            page = self._get_deed_page()
            rows = page.find_all('tr')
            for row in rows:
                if 'Property Owner' in row.text:
                    defs = row.find_all('td')
                    assert('Property Owner' in defs[1].text)
                    # owner text is in subsequent <td> elements, until 'Use the Deeds link' <td>
                    owners = []
                    for idx in range(2, len(defs)):
                        cell_text = defs[idx].text
                        if 'Use the Deeds' in cell_text:
                            break
                        owner = cell_text.strip()
                        if len(owner):
                            owners.append(cell_text.strip())
                    self._owner = '; '.join(owners)
                    break
        assert(self._owner is not None)
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
            result = int(''.join([c for c in str(self._heated_area) if c != ',']))
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

    @property
    def deed_url(self):
        return self._deed_url

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
    def __init__(self, csv_filename):
        self._apts = None
        self._csv_filename = csv_filename
        self._get_current_csv()

    def get_canonical_apts(self):
        x = sorted(self.apts, key=operator.attrgetter('st_num'))
        return sorted(x, key=operator.attrgetter('account'))

    def _get_current_csv(self):
        self._prev_acct_map = {}
        ignore_dups = ['0076203']
        try:
            with open(self._csv_filename) as csv_file:
                rdr = csv.DictReader(csv_file)
                for row in rdr:
                    #TODO: Use acct # to identify units and homes
                    acct = row['account']
                    if acct in self._prev_acct_map and acct in ignore_dups:
                        logging.error(f"Duplicate accounts: {acct}")
                    else:
                        self._prev_acct_map[acct] = dict(row)
        except Exception as err:
            logging.error(f"ERROR: {err}")

    @property
    def apts(self) -> list:
        if self._apts is None:
            self._apts = []
            self.wake_search()
        return self._apts

    def wake_search(self):
        for base_url in [f'http://services.wakegov.com/realestate/AddressSearch.asp?stnum=&stype=addr&stname=cypress+club&locidList=',
                         f'http://services.wakegov.com/realestate/AddressSearch.asp?stnum=&stype=addr&stname=cypress+lakes&locidList=',
                         ]:
            self.search_apts(base_url)

    def search_apts(self, base_url):
        # Note: need to iterate through all the pages; use page_num for url parm
        page_num = 1
        while True:
            apt_count = 0
            page = requests.get(f"{base_url}&spg={page_num}")
            soup = BeautifulSoup(page.content, 'html.parser')
            # search thru all tr looking for good results
            for row in soup.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) < 9 or not(represents_int(cols[2].text)):
                    continue
                account = cols[1].text
                unit = cols[3].text
                st_num = cols[2].text
                st_name = cols[5].text
                if unit != '' or st_num != '':
                    self._apts.append(Apt(account, unit, st_num, st_name))
                    apt_count += 1
            if apt_count == 0:
                break
            page_num += 1
        logging.info(f"Found {len(self._apts)} units online")
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

    def get_account(self, acct_str):
        for apt in self.apts:
            if apt.account == acct_str:
                return apt
        return None
    def get_unit(self, unit_str):
        for apt in self.apts:
            if apt.unit == unit_str:
                return apt
        return None
    
    def check_missing(self):
        curr_accts = set(map(lambda x: x.account, list(self.apts)))
        prev_accts = set(self._prev_acct_map.keys())
        self._deleted_accts = prev_accts - curr_accts
        if len(self._deleted_accts):
            logging.warning(f"Deleted: {', '.join(sorted(self._deleted_accts))}")
        added = curr_accts - prev_accts
        if len(added):
            logging.warning(f"Added: {', '.join(sorted(added))}")

    def make_csv(self):
        with open(self._csv_filename, "w", newline='') as fp:
            field_names = ['st_num', 'unit_num', 'owner', 'heated_area', 'deed_date', 'pkg_sale_price', 'assessed', 'account', 'photo', 'st_name', 'style', 'model']
            writer = csv.DictWriter(fp, fieldnames=field_names, quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
#            for apt in sorted(self.apts, key=lambda x: x.unit):
            for apt in self.get_canonical_apts():
                writer.writerow({'st_num': apt.st_num, 'unit_num': apt.unit, 
                    'owner': apt.owner, 'heated_area': apt.heated_area, 
                    'deed_date': apt.deed_date.strftime('%m/%d/%Y'), 'pkg_sale_price': apt.pkg_sale_price, 
                    'assessed': apt.assessed, 'account': apt.account, 'photo': 'photo', 'st_name': apt.st_name, 'style': apt.style, 'model': apt.model})

def print_apts(apts, fn, title=''):
    with open(fn, 'w') as fp:
        print(f"\n{title}\n\n", file=fp)
        for apt in apts:
            # Improve owner field by converting newlines into semi-colons
            print("-----------------------", file=fp)
            print(f"Street Number: {apt.st_num}", file=fp)
            print(f"Unit: {apt.unit}\tOwner: {apt.owner}", file=fp)
            print(f"Heated Area: {apt.heated_area}", file=fp)
            print(f"Deed Date: {apt.deed_date.strftime('%m/%d/%Y')}", file=fp)
            print(f"Pkg Sale Price: {apt.pkg_sale_price}", file=fp)
            print(f"Assessed: {apt.assessed}", file=fp)
            print(f"Account: {apt.account}", file=fp)
        fp.close()

def represents_int(s):
    try: 
        int(s)
    except ValueError:
        return False
    else:
        return True

def main():
    logging.basicConfig(filename='./reports/cypress/cypress_deeds.log', level=logging.INFO,
                        format='%(levelname)s\t%(message)s', filemode='w')
    logging.info("Start")
    csv_filename = "./reports/cypress/cypress.csv"
    ctlr = Apts(csv_filename)
    ctlr.apts
    ctlr.check_missing()
    ctlr.make_csv()
    #print_apts(ctlr.by_unit_num(), "./reports/cypress/by_unit.txt", "By Unit")
    #print_apts(ctlr.by_deed_date(reverse=True), "./reports/cypress/by_deed.txt", "By Deed Date")
    #print_apts(ctlr.by_heated_area(reverse=True), "./reports/cypress/by_heated_area.txt", "By Heated Area")
    logging.info("Done")

def fix_python():
    if sys.platform == 'win32':
        #This is required in order to make pyuno usable with the default python interpreter under windows
        #Some environment variables must be modified

        #get the install path from registry
        import winreg
        install_folder = None
        # try with OpenOffice, LibreOffice on W7
        for _key in [# OpenOffice 3.3
                    "SOFTWARE\\LibreOffice\\UNO\\InstallPath",
                    # LibreOffice 3.4.5 on W7
                    "SOFTWARE\\Wow6432Node\\LibreOffice\\UNO\\InstallPath"]:
            try:
                value = winreg.QueryValue(winreg.HKEY_LOCAL_MACHINE, _key)
                install_folder = '\\'.join(value.split('\\')[:-1]) # 'C:\\Program Files\\OpenOffice.org 3'
                #modify the environment variables
                os.environ['URE_BOOTSTRAP'] = 'vnd.sun.star.pathname:{0}\\program\\fundamental.ini'.format(install_folder)
                os.environ['UNO_PATH'] = install_folder+'\\program\\'

                sys.path.append(install_folder+'\\Basis\\program')
                sys.path.append(install_folder+'\\program')

                paths = ''
                for path in ("\\URE\\bin;", "\\Basis\\program;", "'\\program;"):
                    paths += install_folder + path
                os.environ['PATH'] =  paths+ os.environ['PATH']
            except Exception as detail:
                _errMess = "%s" % detail
            else:
                break   # first existing key will do

if __name__ == '__main__':
    main()
