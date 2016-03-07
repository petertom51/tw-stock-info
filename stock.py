import requests
import sqlite3
from bs4 import BeautifulSoup

TWSE = 1
OTC  = 2

class Stock:

    _filename = ''
    _table_name = 'stocks'
    _connection = None

    def __enter__(self):
        self._connection = sqlite3.connect(self._filename)
        cursor = self._connection.cursor()
        sql_cmd = 'CREATE TABLE IF NOT EXISTS ' + self._table_name + '(ID text primary key, NAME text, MARKET integer)'
        cursor.execute(sql_cmd)
        self._connection.commit()

        cursor.execute('select * from stocks')
        if cursor.fetchone() is None:
            self._collect_stock_info()

        return self

    def __exit__(self, type, value, traceback):
        self._connection.close()

    def __init__(self, filename):
        self._create_file(filename)
        self._filename = filename;

    def _create_file(self, filename):
        open(filename, 'a').close()

    def is_stock_id_exist(self, stock_no):
        cursor = self._connection.cursor()
        sql_cmd = 'SELECT * FROM {} WHERE ID = {}'.format(self._table_name, stock_no)
        cursor.execute(sql_cmd)
        if cursor.fetchone() is None:
            # A chance to add new stock info
            self._collect_stock_info(stock_no)
            cursor.execute(sql_cmd)
            if cursor.fetchone() is None:
                return False
        return True

    def _get_stocks(self, url, market, stock_no=None):
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for row in soup.find_all('tr')[1:]:
            col = row.find_all('td')
            id = col[2].string.strip()
            if stock_no is None or stock_no == id:
                name = col[3].string.strip()
                cursor = self._connection.cursor()
                sql_cmd = 'INSERT INTO {} VALUES (?, ?, ?)'.format(self._table_name)
                cursor.execute(sql_cmd, (id, name, market))
        self._connection.commit()

    def _collect_stock_info(self, stock_no=None):
        ''' get all stock id from otc and twse '''
        twse_stock_list_url = 'http://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y'
        self._get_stocks(twse_stock_list_url, TWSE, stock_no)

        otc_stock_list_url = 'http://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=4&industry_code=&Page=1&chklike=Y'
        self._get_stocks(otc_stock_list_url, OTC, stock_no)
        pass

