import unittest
from stock import *
from os import path, remove


class PriceTestCase(unittest.TestCase):
    
    def setUp(self):
        self.db_file = './test.db'

    def tearDown(self):
        pass

    def test_check_file_existed(self):
        with Stock(self.db_file):
            self.assertTrue(path.isfile(self.db_file))

    def test_is_stock_id_exist(self):
        with Stock(self.db_file) as stock:
            self.assertFalse(stock.is_stock_id_exist('0050')) 
            self.assertTrue(stock.is_stock_id_exist('1101')) # 台泥
            self.assertTrue(stock.is_stock_id_exist('5601')) # 台聯櫃

    def test_get_price_nonexist_stock_id(self):
        with Stock(self.db_file) as stock:
            self.assertIsNone(stock.get_price('0050'))

    def test_get_price(self):
        with Stock(self.db_file) as stock:
            self.assertIsInstance(stock.get_price('1101'), float)
            self.assertIsInstance(stock.get_price('5601'), float)

    def test_collect_stock_info(self):
        remove(self.db_file)
        stock = Stock(self.db_file)
        stock.collect_stock_info()
        self.assertFalse(stock.is_stock_id_exist('0050')) 
        self.assertTrue(stock.is_stock_id_exist('1101')) # 台泥
        self.assertTrue(stock.is_stock_id_exist('5601')) # 台聯櫃

if __name__ == '__main__':
    unittest.main()

