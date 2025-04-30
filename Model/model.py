import datetime
from threading import Timer


class Model:
    holidays = [
        "05-01", "05-02", "05-03", "05-04",
        "05-08", "05-09", "05-10", "05-11"
    ]

    def calculate_payment(month_options, year_var, month_var, day_var, time_var, product_type_var, product_var, people_count_var, percentage_entry_var, payment_type_var, actuallPayment, payLabel):
        total_price = 0
        is_holiday = False
        try:
            # Получить дату и время из введенных значений
            selected_date = datetime.date(
                int(year_var.get()),
                # Индексация месяцев начинается с 0
                month_options.index(month_var.get()) + 1,
                int(day_var.get())
            )
            print(f"выбранная дата:{selected_date}")
            # Проверить, является ли дата праздничной
            if selected_date.strftime("%m-%d") in Model.holidays:
                is_holiday = True
            selected_time = datetime.datetime.strptime(
                time_var.get(), "%H:%M").time()
            # Get the day of the week number (0=Monday, 6=Sunday)
            day_of_week = selected_date.weekday()
            print(day_of_week)
            # Базовая цена для обычных игр
            if selected_date.weekday() >= 4 or is_holiday:  # 5 и 6 соответствуют субботе и воскресенью, 4 — пятница
                AWgame_price = 1800  # Увеличить базовую цену для выходных
            else:
                if selected_time >= datetime.time(16, 0):
                    AWgame_price = 1600  # Увеличить базовую цену для вечерних часов
                else:
                    AWgame_price = 1400  # Базовая цена для будних дней

            # Базовая цена для одиночных игр за 15 минут
            AloneGamePrice = 450

            if product_type_var.get() == "Время":
                people_count = int(people_count_var.get(
                )) if people_count_var.get().isdigit() else 1
                hrsofplaytime = int(
                    product_var.get().split(" ")[0]) / 60
                percentage = int(percentage_entry_var.get()) if payment_type_var.get() in [
                    "Доплата", "Предоплата"] and percentage_entry_var.get().isdigit() else 0

                total_price = AWgame_price * people_count * hrsofplaytime
                if percentage > 0:
                    total_price = total_price * (percentage / 100)

            elif product_type_var.get() == "Тариф":
                product_var.get()
                selected_time = datetime.datetime.strptime(
                    time_var.get(), "%H:%M").time()

                # Check if the selected date is a weekend
                # 5 and 6 correspond to Saturday and Sunday
                is_weekend = selected_date.weekday() >= 4
                print(selected_date.weekday())
                is_evening = selected_time >= datetime.time(16, 0)

                percentage = int(percentage_entry_var.get()) if payment_type_var.get() in [
                    "Доплата", "Предоплата"] and percentage_entry_var.get().isdigit() else 0
                # Adjust price based on weekend, evening, and tariff
                if product_var.get() == "STD":
                    total_price = 25000 if is_weekend or is_holiday else \
                        20000 if is_evening or is_holiday else 15000
                elif product_var.get() == "HARD":
                    total_price = 35000 if is_weekend or is_holiday else \
                        27500 if is_evening else 20000
                elif product_var.get() == "VIP":
                    total_price = 45000 if is_weekend or is_holiday else \
                        35000 if is_evening else 25000
                if percentage > 0:
                    total_price = total_price * (percentage / 100)

            elif product_type_var.get() == "Одиночная игра":
                product_var.get()
                people_count = int(people_count_var.get(
                )) if people_count_var.get().isdigit() else 1
                percentage = int(percentage_entry_var.get()) if payment_type_var.get() in [
                    "Доплата", "Предоплата"] and percentage_entry_var.get().isdigit() else 0
                hrsofplaytime = int(
                    product_var.get().split(" ")[0]) / 15
                total_price = AloneGamePrice * people_count * hrsofplaytime
                if percentage > 0:
                    total_price = total_price * (percentage / 100)

            elif product_type_var.get() == "Абонемент":
                subscription_price = int(product_var.get().split(" ")[
                    1])  # Extract price from string
                percentage = int(percentage_entry_var.get()) if payment_type_var.get() in [
                    "Доплата", "Предоплата"] and percentage_entry_var.get().isdigit() else 0
                total_price = subscription_price
                if percentage > 0:
                    total_price = total_price * (percentage / 100)

            elif product_type_var.get() == "Сертификат":
                certificate_price = int(product_var.get().split(" ")[
                                        1])  # Extract price from string
                percentage = int(percentage_entry_var.get()) if payment_type_var.get() in [
                    "Доплата", "Предоплата"] and percentage_entry_var.get().isdigit() else 0
                total_price = certificate_price
                if percentage > 0:
                    total_price = total_price * (percentage / 100)
            actuallPayment.set(total_price)

            payLabel.config(
                text=f"Рассчитанная \n стоимость: {actuallPayment.get()}")

        except ValueError as e:
            payLabel.config(text="Ошибка в расчетах")
            print(f"Error is {e}")

            def clear_label():
                payLabel.config(text="")
            Timer(1.5, clear_label).start()
