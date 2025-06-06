import datetime
from threading import Timer


class Model:
    """
    Model class for calculating payment amounts based on various product types and user selections.

    Class Attributes:
        allowed_macs (list): List of allowed MAC addresses for authentication.
        allowed_hosts (list): List of allowed hostnames for authentication.
        hashed_password (str): Hashed password for authentication.
    Methods:
        calculate_payment(
            month_options,
            year_var,
            month_var,
            day_var,
            time_var,
            product_type_var,
            product_var,
            people_count_var,
            percentage_entry_var,
            payment_type_var,
            actuallPayment,
            payLabel
        ):
            Calculates the total payment based on the selected date, time, product type, product, number of people, percentage (for prepayment or additional payment), and payment type.
            Updates the actuallPayment variable and payLabel widget with the calculated amount.
            Handles different product types: "Время" (Time), "Тариф" (Tariff), "Одиночная игра" (Single Game), "Абонемент" (Subscription), and "Сертификат" (Certificate).
            Displays an error message in payLabel if calculation fails due to invalid input.
    """

    allowed_macs = ["5e894cf837ed457b3f1debf8cfd911f14df0d05ab27415125d1ec2593a21e2b3"]
    allowed_hosts = ["Danyas-MacBook-Pro.local"]
    hashed_password = "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"
    def calculate_payment(month_options, year_var, month_var, day_var, time_var, product_type_var, product_var, people_count_var, percentage_entry_var, payment_type_var, actuallPayment, payLabel):
        """
        Calculates the payment amount based on selected date, time, product type, and other user inputs, 
        and updates the provided actuallPayment variable and payLabel widget with the result.
        Parameters:
            month_options (list): List of month names for mapping month_var to a month index.
            year_var (tkinter.Variable): Variable holding the selected year as a string.
            month_var (tkinter.Variable): Variable holding the selected month as a string.
            day_var (tkinter.Variable): Variable holding the selected day as a string.
            time_var (tkinter.Variable): Variable holding the selected time as a string in "%H:%M" format.
            product_type_var (tkinter.Variable): Variable holding the selected product type.
            product_var (tkinter.Variable): Variable holding the selected product or product details.
            people_count_var (tkinter.Variable): Variable holding the number of people as a string.
            percentage_entry_var (tkinter.Variable): Variable holding the percentage for partial payments as a string.
            payment_type_var (tkinter.Variable): Variable holding the type of payment ("Доплата", "Предоплата", etc.).
            actuallPayment (tkinter.Variable): Variable to be updated with the calculated payment amount.
            payLabel (tkinter.Label): Label widget to display the calculated payment or error messages.
        Behavior:
            - Determines the price based on the product type, date, time, and other parameters.
            - Applies a percentage if the payment type is partial.
            - Updates actuallPayment with the calculated price.
            - Updates payLabel with the result or an error message if calculation fails.
        """
        
        total_price = 0
        try:
            selected_date = datetime.date(
                int(year_var.get()),
                month_options.index(month_var.get()) + 1,
                int(day_var.get())
            )
            selected_time = datetime.datetime.strptime(
                time_var.get(), "%H:%M").time()
            day_of_week = selected_date.weekday()
            if selected_date.weekday() >= 4:  
                AWgame_price = 1800  
            else:
                if selected_time >= datetime.time(16, 0):
                    AWgame_price = 1600 
                else:
                    AWgame_price = 1400 
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


                is_weekend = selected_date.weekday() >= 4
                is_evening = selected_time >= datetime.time(16, 0)

                percentage = int(percentage_entry_var.get()) if payment_type_var.get() in [
                    "Доплата", "Предоплата"] and percentage_entry_var.get().isdigit() else 0
                if product_var.get() == "STD":
                    total_price = 25000 if is_weekend else \
                        20000 if is_evening else 15000
                elif product_var.get() == "HARD":
                    total_price = 35000 if is_weekend else \
                        27500 if is_evening else 20000
                elif product_var.get() == "VIP":
                    total_price = 45000 if is_weekend else \
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
                    1])  
                percentage = int(percentage_entry_var.get()) if payment_type_var.get() in [
                    "Доплата", "Предоплата"] and percentage_entry_var.get().isdigit() else 0
                total_price = subscription_price
                if percentage > 0:
                    total_price = total_price * (percentage / 100)

            elif product_type_var.get() == "Сертификат":
                certificate_price = int(product_var.get().split(" ")[
                                        1])  
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
