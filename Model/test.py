import unittest
from unittest.mock import MagicMock
from model import Model

class DummyVar:
    def __init__(self, value):
        self._value = value
    def get(self):
        return self._value
    def set(self, value):
        self._value = value

class DummyLabel:
    def __init__(self):
        self.text = ""
    def config(self, text):
        self.text = text

class TestModelCalculatePayment(unittest.TestCase):
    def setUp(self):
        self.month_options = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]

    def test_tariff_std_weekend(self):
        year = DummyVar("2024")
        month = DummyVar("Март")
        day = DummyVar("16")  
        time = DummyVar("15:00")
        product_type = DummyVar("Тариф")
        product = DummyVar("STD")
        people_count = DummyVar("1")
        percentage = DummyVar("")
        payment_type = DummyVar("Полная оплата")
        actuallPayment = DummyVar(0)
        payLabel = DummyLabel()
        Model.calculate_payment(
            self.month_options, year, month, day, time, product_type, product,
            people_count, percentage, payment_type, actuallPayment, payLabel
        )
        self.assertEqual(actuallPayment.get(), 25000)
        self.assertIn("25000", payLabel.text)

    def test_time_evening_weekday(self):
        year = DummyVar("2024")
        month = DummyVar("Март")
        day = DummyVar("13")  
        time = DummyVar("17:00")
        product_type = DummyVar("Время")
        product = DummyVar("60 мин")
        people_count = DummyVar("2")
        percentage = DummyVar("")
        payment_type = DummyVar("Полная оплата")
        actuallPayment = DummyVar(0)
        payLabel = DummyLabel()
        Model.calculate_payment(
            self.month_options, year, month, day, time, product_type, product,
            people_count, percentage, payment_type, actuallPayment, payLabel
        )

        self.assertEqual(actuallPayment.get(), 3200)
        self.assertIn("3200", payLabel.text)

    def test_single_game_partial_payment(self):
        year = DummyVar("2024")
        month = DummyVar("Март")
        day = DummyVar("13")
        time = DummyVar("12:00")
        product_type = DummyVar("Одиночная игра")
        product = DummyVar("15 мин")
        people_count = DummyVar("3")
        percentage = DummyVar("50")
        payment_type = DummyVar("Доплата")
        actuallPayment = DummyVar(0)
        payLabel = DummyLabel()
        Model.calculate_payment(
            self.month_options, year, month, day, time, product_type, product,
            people_count, percentage, payment_type, actuallPayment, payLabel
        )
        # 450 * 3 * 1 = 1350, 50% = 675
        self.assertEqual(actuallPayment.get(), 675)
        self.assertIn("675", payLabel.text)

    def test_subscription(self):
        year = DummyVar("2024")
        month = DummyVar("Март")
        day = DummyVar("13")
        time = DummyVar("12:00")
        product_type = DummyVar("Абонемент")
        product = DummyVar("За 2500 рублей")
        people_count = DummyVar("1")
        percentage = DummyVar("")
        payment_type = DummyVar("Полная оплата")
        actuallPayment = DummyVar(0)
        payLabel = DummyLabel()
        Model.calculate_payment(
            self.month_options, year, month, day, time, product_type, product,
            people_count, percentage, payment_type, actuallPayment, payLabel
        )
        self.assertEqual(actuallPayment.get(), 2500)
        self.assertIn("2500", payLabel.text)

    def test_certificate_with_percentage(self):
        year = DummyVar("2024")
        month = DummyVar("Март")
        day = DummyVar("13")
        time = DummyVar("12:00")
        product_type = DummyVar("Сертификат")
        product = DummyVar("На 3000 рублей")
        people_count = DummyVar("1")
        percentage = DummyVar("25")
        payment_type = DummyVar("Предоплата")
        actuallPayment = DummyVar(0)
        payLabel = DummyLabel()
        Model.calculate_payment(
            self.month_options, year, month, day, time, product_type, product,
            people_count, percentage, payment_type, actuallPayment, payLabel
        )

        self.assertEqual(actuallPayment.get(), 750)
        self.assertIn("750", payLabel.text)

    def test_invalid_input(self):
        year = DummyVar("2024")
        month = DummyVar("Март")
        day = DummyVar("bad_day")
        time = DummyVar("12:00")
        product_type = DummyVar("Сертификат")
        product = DummyVar("На 3000 рублей")
        people_count = DummyVar("1")
        percentage = DummyVar("25")
        payment_type = DummyVar("Предоплата")
        actuallPayment = DummyVar(0)
        payLabel = DummyLabel()
        Model.calculate_payment(
            self.month_options, year, month, day, time, product_type, product,
            people_count, percentage, payment_type, actuallPayment, payLabel
        )
        self.assertIn("Ошибка", payLabel.text)

if __name__ == "__main__":
    unittest.main()
