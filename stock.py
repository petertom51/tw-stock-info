import requests
import sqlite3
import json
import time
from bs4 import BeautifulSoup

TSE = 'tse'
OTC  = 'otc'

class Stock:
    ''' When it new an instance, it will check if the database exist first. 
        If not, it collects all stock id and creates a database for it. '''

    _filename = ''
    _table_name = 'stocks'
    _connection = None

    def __enter__(self):
        self._connection = sqlite3.connect(self._filename)
        cursor = self._connection.cursor()
        sql_cmd = 'CREATE TABLE IF NOT EXISTS ' + self._table_name + '(ID text primary key, NAME text, MARKET text)'
        cursor.execute(sql_cmd)
        self._connection.commit()

        cursor.execute('select * from stocks')
        if cursor.fetchone() is None:
            self.collect_stock_info()

        return self

    def __exit__(self, type, value, traceback):
        self._connection.close()

    def __init__(self, filename):
        self._prepare_file(filename)
        self._filename = filename;

    def _is_sqlite3_db(filename):
        from os.path import isfile, getsize

        if not isfile(filename) or getsize(filename) < 100:
            return False

        with open(filename, 'rb') as file:
            header = file.read(100)

        return header[:16] == b'SQLite format 3\x00'

    def _prepare_file(self, filename):
        open(filename, 'a').close()


    def _get_stocks(self, url, stock_no=None, market=None):
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for row in soup.find_all('tr')[1:]:
            col = row.find_all('td')
            id = col[2].string.strip()
            if stock_no is None or stock_no == id:
                name = col[3].string.strip()
                if not self._connection:
                    self._connection = sqlite3.connect(self._filename)
                cursor = self._connection.cursor()
                sql_cmd = 'INSERT INTO {} VALUES (?, ?, ?)'.format(self._table_name)
                cursor.execute(sql_cmd, (id, name, market))
        self._connection.commit()

    def collect_stock_info(self, stock_no=None):
        ''' get all stock id from otc and twse '''
        twse_stock_list_url = 'http://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y'
        self._get_stocks(twse_stock_list_url, stock_no, TSE)

        otc_stock_list_url = 'http://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=4&industry_code=&Page=1&chklike=Y'
        self._get_stocks(otc_stock_list_url, stock_no, OTC)
        pass

    def is_stock_id_exist(self, stock_no):
        cursor = self._connection.cursor()
        sql_cmd = 'SELECT * FROM {} WHERE ID = {}'.format(self._table_name, stock_no)
        cursor.execute(sql_cmd)
        if cursor.fetchone() is None:
            return False
        return True

    def get_price(self, stock_no):
        ''' Get stock price by stock id '''
        if not self.is_stock_id_exist(stock_no):
            return None

        cursor = self._connection.cursor()
        sql_cmd = 'SELECT * FROM {} WHERE ID={}'.format(self._table_name, stock_no)
        cursor.execute(sql_cmd)
        market = cursor.fetchone()[2]

        req = requests.session()
        req.get('http://mis.twse.com.tw/stock/index.jsp') # Get session info
        query_url = 'http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={}_{}.tw&json=1'
        response = req.get(query_url.format(market, stock_no))
        
        json_obj = json.loads(response.text)

        try:
            lastest_price = json_obj['msgArray'][0]['z']
        except KeyError as e:
            lastest_price = json_obj['msgArray'][0]['y']
        except:
            lastest_price = 0.0

        return float(lastest_price)
    

