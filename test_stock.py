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


if __name__ == '__main__':
    unittest.main()

