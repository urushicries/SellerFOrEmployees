import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd


sys.modules['Model'] = MagicMock()
sys.modules['Model.FFCWP'] = MagicMock()

from Update.updater import Updater

class DummyUI:
    def __init__(self):
        self.employee_request = [["Иванов", "Оператор", "1"], "Коменда"]

class TestUpdater(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_sheet = MagicMock()
        self.mock_sheet.update = MagicMock()
        self.mock_sheet.batch_update = MagicMock()
        self.mock_sheet.col_values = MagicMock(return_value=["06.06.2025"])
        self.mock_sheet.get = MagicMock(return_value=[["data"]])
        self.config = {
            'client': self.mock_client,
            'sheetPIK': self.mock_sheet,
            'sheetJUN': self.mock_sheet,
            'sheetLM': self.mock_sheet,
            'sheetKOM': self.mock_sheet,
            'sheetWAGES': self.mock_sheet,
        }
        self.updater = Updater(self.config)
        self.updater.ui = DummyUI()
        self.updater.employee_list = [["Иванов", "Оператор", "1"], "Коменда"]

    def test_get_last_item(self):
        result = self.updater.get_last_item(["a", "b", "Коменда"])
        self.assertEqual(result, self.mock_sheet)

    def test_getCellAddrToday(self):
        addr = self.updater.getCellAddrToday(self.mock_sheet)
        self.assertTrue(addr is None or addr.startswith("A"))

    def test_update_sheet_wEmp(self):
        self.updater.update_sheet_wEmp(self.mock_sheet, [["Иванов", "Оператор", "1"]], "A1")
        self.mock_sheet.update.assert_called()

    def test_add_new_sell(self):
        payment_request = {
            "Тип товара": "Тариф",
            "Товар": "STD",
            "Время чека": "12:00",
            "Количество человек": "2",
            "Карта": "1000",
            "QR/СБП": "500",
            "Наличные по кассе": "0",
            "НП": "0",
            "Игра AW": "0",
            "Комментарий": "test"
        }
        self.updater.add_new_sell(self.mock_sheet, "A2", payment_request)
        self.mock_sheet.batch_update.assert_called()


if __name__ == "__main__":
    unittest.main()
