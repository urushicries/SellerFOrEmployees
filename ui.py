import tkinter as tk
from threading import Timer
import hashlib
import datetime
import sys


class UIManager:

    def __init__(self, config):
        root = config['root']
        sheetwages = config['sheetWAGES']
        employees = config.get('employees', [])
        self.updater = config['Updater']
        employees.append("Пропуск")
        self.resize_timer = None  # Timer for debouncing
        self.sheetwages = sheetwages
        self.employees = config['list_employee']
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # Adjust scaling for better appearance
        self.root.tk.call("tk", "scaling", 1.0)
        self.root.option_add("*Font", "Helvetica 14")  # Set default font
        # Flat buttons for macOS look
        self.root.option_add("*Button.relief", "flat")
        self.root.option_add("*Button.highlightThickness",
                             0)  # Remove button border

        # Light gray button background
        self.root.option_add("*Button.background", "#E8E8E8")
        # Slightly darker gray for active buttons
        self.root.option_add("*Button.activeBackground", "#D0D0D0")
        # Light gray background for labels
        self.root.option_add("*Label.background", "#F0F0F0")
        # Black text for labels
        self.root.option_add("*Label.foreground", "#000000")
        # White background for entry fields
        self.root.option_add("*Entry.background", "#FFFFFF")
        # Black text for entry fields
        self.root.option_add("*Entry.foreground", "#000000")
        # Thin border for entry fields
        self.root.option_add("*Entry.highlightThickness", 1)
        self.root.iconbitmap("aw.ico")
        self.root.configure(bg="#000000")  # Set root background to light gray
        self.root.title("Заполнение отчета")
        self.frames = {}
        self.today_date = datetime.date.today()
        self.address = None
        self.employee_request = None
        # Initialize frames
        self.init_login_frame()
        self.init_employee_frame()
        self.init_payment_frame()
        self.init_summary_frame()
        self.show_frame("login_frame")
        self.wrongAttempts = 0

    def on_close(self):
        """Handle window close event."""
        # Cancel the resize timer if it exists
        if self.resize_timer:
            self.resize_timer.cancel()

        # Stop the mainloop and destroy the root window
        self.root.quit()
        self.root.destroy()

        # Exit the program completely
        sys.exit(0)

    def enforce_frame_size(self, event):
        """Debounce the frame size enforcement."""
        # Cancel any existing timer
        if self.resize_timer:
            self.resize_timer.cancel()

        # Start a new timer to delay execution
        self.resize_timer = Timer(0.1, self._apply_frame_size)
        self.resize_timer.start()

    def _apply_frame_size(self):
        """Quickly apply the frame size logic after debounce delay."""
        for frame_name, frame in self.frames.items():
            if frame.winfo_ismapped():
                target_geometry = None
                if frame_name == "payment_frame":
                    target_geometry = (1000, 650)
                elif frame_name == "employee_frame":
                    target_geometry = (590, 310)
                elif frame_name == "login_frame":
                    target_geometry = (300, 300)
                elif frame_name == "summary_frame":
                    target_geometry = (480, 180)

                if target_geometry:
                    current_geometry = self.root.geometry()
                    # Extract width and height, ignoring position offsets
                    current_width, current_height = map(
                        int, current_geometry.split("+")[0].split("x"))
                    target_width, target_height = target_geometry

                    # Fewer steps for quicker resizing
                    width_step = (target_width - current_width) / 100
                    height_step = (target_height - current_height) / 100

                    def animate_resize(step=0):
                        if step <= 100:  # Reduce total steps
                            new_width = int(current_width + width_step * step)
                            new_height = int(
                                current_height + height_step * step)
                            self.root.geometry(f"{new_width}x{new_height}")
                            # Slightly longer delay for smoother animation
                            self.root.after(5, animate_resize, step + 1)

                    animate_resize()

    def init_login_frame(self):
        frame = tk.Frame(self.root)
        self.frames["login_frame"] = frame
        frame.configure(bg="#000000")  # Set frame background to black
        frame.option_add("*Font", "Helvetica 14")  # Set default font
        # Flat buttons for macOS look
        frame.option_add("*Button.relief", "flat")
        frame.option_add("*Button.highlightThickness",
                         0)  # Remove button border
        # Dark gray button background
        frame.option_add("*Button.background", "#FFFFFF")
        # White text for buttons
        frame.option_add("*Button.foreground", "#000000")
        # Slightly lighter gray for active buttons
        frame.option_add("*Button.activeBackground", "#555555")
        # Black background for labels
        frame.option_add("*Label.background", "#000000")
        # White text for labels
        frame.option_add("*Label.foreground", "#FFFFFF")
        # Dark gray background for entry fields
        frame.option_add("*Entry.background", "#333333")
        # White text for entry fields
        frame.option_add("*Entry.foreground", "#FFFFFF")
        # Thin border for entry fields
        frame.option_add("*Entry.highlightThickness", 1)
        tk.Label(frame, text="Введите логин и пароль").grid(
            row=0, column=0, columnspan=2, pady=10)

        tk.Label(frame, text="Логин").grid(row=1, column=0, pady=5)
        self.username_var = tk.StringVar(frame)
        tk.Entry(frame, textvariable=self.username_var).grid(
            row=1, column=1, pady=5)

        tk.Label(frame, text="Пароль").grid(row=2, column=0, pady=5)
        self.password_var = tk.StringVar(frame)
        password_entry = tk.Entry(
            frame, textvariable=self.password_var, show="*")
        password_entry.grid(row=2, column=1, pady=5)

        footerLabel = tk.Label(
            frame, text="Все довольно просто\n Вводите логин и пароль и кайфуете", font=("Helvetica", 10))
        footerLabel.grid(row=999, column=0, columnspan=2, pady=5, sticky="s")
        # Ensure the footer stays at the bottom
        frame.grid_rowconfigure(999, weight=1)

        def paste_password():
            try:
                clipboard_content = self.root.clipboard_get()
                self.password_var.set(clipboard_content)
            except tk.TclError:
                pass  # Handle empty clipboard gracefully

        password_menu = tk.Menu(self.root, tearoff=0)
        password_menu.add_command(label="Paste", command=paste_password)

        def show_password_menu(event):
            password_menu.post(event.x_root, event.y_root)

        password_entry.bind("<Button-3>", show_password_menu)

        tk.Button(frame, text="Войти", command=self.validate_login).grid(
            row=3, column=0, columnspan=2, pady=10)

    def validate_login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        # Store credentials securely using a hashed password

        # Replace these with your actual username and hashed password
        usernamer = "spb-aw"
        passwordr = "fc17f007ddcf314128317bbed059ae8b253176d0dd846243627492f215121a5c"

        # Hash the input password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Placeholder for actual login validation logic
        if username == usernamer and hashed_password == passwordr:
            self.show_frame("employee_frame")
        else:
            error_text = "Неверный логин и пароль" if username != usernamer and hashed_password != passwordr else \
                "Неверный логин" if username != usernamer else "Неверный пароль"
            error_message = tk.Label(
                self.frames["login_frame"], text=error_text, fg="red")
            error_message.grid(row=4, column=0, columnspan=2, pady=5)
            self.root.after(1500, error_message.destroy)
            self.wrongAttempts += 1
            attempts_left = 3 - self.wrongAttempts
            tk.Label(self.frames["login_frame"], text=f"Осталось попыток: {attempts_left}", fg="red").grid(
                row=5, column=0, columnspan=2, pady=5)
            if self.wrongAttempts == 3:
                self.on_close()

    def init_employee_frame(self):
        # Set frame background to black
        frame = tk.Frame(self.root, bg="#000000")
        self.frames["employee_frame"] = frame

        frame.configure(bg="#000000")  # Set frame background to black
        self.root.configure(bg="#000000")  # Set root background to light gray
        frame.option_add("*Font", "Helvetica 14")  # Set default font
        # Flat buttons for macOS look
        frame.option_add("*Button.relief", "flat")
        frame.option_add("*Button.highlightThickness",
                         0)  # Remove button border
        # Dark gray button background
        frame.option_add("*Button.background", "#333333")
        # White text for buttons
        frame.option_add("*Button.foreground", "#FFFFFF")
        # Slightly lighter gray for active buttons
        frame.option_add("*Button.activeBackground", "#555555")
        # Black background for labels
        frame.option_add("*Label.background", "#000000")
        # White text for labels
        frame.option_add("*Label.foreground", "#FFFFFF")
        # Dark gray background for entry fields
        frame.option_add("*Entry.background", "#333333")
        # White text for entry fields
        frame.option_add("*Entry.foreground", "#FFFFFF")
        # Thin border for entry fields
        frame.option_add("*Entry.highlightThickness", 1)

        tk.Label(frame, text="Выберете сотрудников на смене").grid(
            row=0, column=1, columnspan=3, pady=10)
        tk.Label(frame, text="Имя работника").grid(
            row=1, column=0, columnspan=1, pady=10)
        tk.Label(frame, text="Тип работника ").grid(
            row=1, column=1, columnspan=1, pady=10)
        tk.Label(frame, text="Тип смены").grid(
            row=1, column=2, columnspan=1, pady=10)
        self.employee_vars = []
        self.employee_menus = []
        dropdown_width = 16  # Set a consistent width for all dropdowns
        for i in range(3):
            employee_var = tk.StringVar(frame)
            employee_var.set("Выберете работника")  # Default value
            employee_var.trace_add("write", lambda *args,
                                   idx=i: self.update_employee_options(idx))
            self.employee_vars.append(employee_var)

            role_var = tk.StringVar(frame)
            role_var.set("Оператор")

            shift_var = tk.StringVar(frame)
            shift_var.set("1")

            employee_menu = tk.OptionMenu(frame, employee_var, *self.employees)
            employee_menu.configure(width=dropdown_width)
            employee_menu.grid(row=i + 2, column=0, padx=10, pady=5)
            self.employee_menus.append(employee_menu)

            role_menu = tk.OptionMenu(frame, role_var, "Оператор",
                                      "Администратор", "Стажер")
            role_menu.configure(width=dropdown_width)
            role_menu.grid(row=i + 2, column=1, padx=10, pady=5)

            shift_menu = tk.OptionMenu(frame, shift_var, *
                                       [f"{i/10}" for i in range(1, 11)])
            shift_menu.configure(width=dropdown_width)
            shift_menu.grid(row=i + 2, column=2, padx=10, pady=5)

            tk.Label(frame, text="Рабочее место").grid(
                row=5, column=0, pady=10)
            self.workplace_var = tk.StringVar(frame)
            self.workplace_var.set("Июнь")  # Default value
            workplace_menu = tk.OptionMenu(
                frame, self.workplace_var, "Июнь", "Пик", "Лондон Молл")
            workplace_menu.configure(width=dropdown_width)
            workplace_menu.grid(row=5, column=1, pady=10)

        tk.Button(frame, text="Далее", command=lambda: self.get_employee_request(), fg="black").grid(
            row=6, column=0, columnspan=2, pady=10)

    def get_employee_request(self):
        """Формирует список данных сотрудников."""
        employee_request = []
        for i in range(3):
            employee_request.append([
                self.employee_vars[i].get(),
                self.frames["employee_frame"].grid_slaves(
                    row=i + 2, column=1)[0].cget("text"),
                self.frames["employee_frame"].grid_slaves(
                    row=i + 2, column=2)[0].cget("text")
            ])
        employee_request.append(self.workplace_var.get())
        print(employee_request)
        employee_request = [
            item for item in employee_request[:-1]
            if item[0] not in ["Пропуск", "Выберете работника"]
        ] + [employee_request[-1]]
        self.show_frame("payment_frame")
        self.address = self.updater.adress
        self.employee_request = employee_request
        self.updater.employee_list = self.employee_request
        self.updater._update_emp()

    def update_employee_options(self, changed_index):
        """Исключает уже выбранных сотрудников в остальных списках."""
        selected = [
            var.get() for var in self.employee_vars
            if var.get() != "Выберете работника" and var.get() != "Пропуск"
        ]
        for i, (var, menu_widget) in enumerate(zip(self.employee_vars, self.employee_menus)):
            menu = menu_widget["menu"]
            # Очищаем меню, пересобираем оставшиеся варианты
            menu.delete(0, "end")
            for emp in self.employees:
                # Позволяем оставить свой выбор, иначе исключаем
                if emp not in selected or emp == var.get():
                    menu.add_command(
                        label=emp,
                        command=lambda value=emp, v=var: v.set(value)
                    )
            # Если текущий выбор больше не допустим, сбрасываем
            if var.get() not in [emp for emp in self.employees if emp not in selected or emp == var.get()]:
                var.set("Выберете работника")

    def init_payment_frame(self):

        self.root.bind("<Configure>", self.enforce_frame_size)
        dropdown_width = 13
        frame = tk.Frame(self.root, bg="black")
        self.frames["payment_frame"] = frame
        for i in range(10):  # Adjust the range as needed for the number of rows
            # Set a fixed height for each row
            frame.grid_rowconfigure(i, minsize=50)
        for j in range(10):  # Adjust the range as needed for the number of columns
            # Set a fixed width for each column
            frame.grid_columnconfigure(j, minsize=100)

        tk.Label(frame, text="Выберите тип оплаты", anchor="w").grid(
            row=2, column=0, pady=10, sticky="w")
        tk.Label(frame, text="Выберите товар", anchor="w").grid(
            row=1, column=0, pady=10, sticky="w")
        self.payment_type_var = tk.StringVar(frame)
        self.payment_type_var.set("Тип оплаты")  # Default
        payment_type_menu = tk.OptionMenu(
            frame, self.payment_type_var, "Доплата", "Предоплата", "Полная оплата")
        payment_type_menu.configure(width=dropdown_width)
        payment_type_menu.grid(row=2, column=1, pady=10)

        tk.Label(frame, text="Выберите Тип товара", anchor="w").grid(
            row=0, column=0, pady=10, sticky="w")
        self.product_type_var = tk.StringVar(frame)
        self.product_type_var.set("Тип товара")  # Default
        product_type_menu = tk.OptionMenu(
            frame, self.product_type_var, "Тариф", "Время", "Одиночная игра", "Абонемент", "Сертификат")
        product_type_menu.configure(width=dropdown_width)
        product_type_menu.grid(row=0, column=1, pady=10)

        self.product_var = tk.StringVar(frame)
        self.product_dropdown = tk.OptionMenu(
            frame, self.product_var, "тут будут продукты")
        self.product_dropdown.configure(width=dropdown_width)
        self.product_dropdown.grid(row=1, column=1, pady=10)
        self.product_type_var.trace_add("write", self.update_dropdown)

        def update_people_count_visibility(*args):

            if self.product_type_var.get() in ["Время", "Одиночная игра"]:
                people_count_label.grid(row=4, column=0, pady=10, sticky="w")
                people_count_entry.grid(row=4, column=1, pady=10)
            else:
                people_count_label.grid_forget()
                people_count_entry.grid_forget()

        people_count_label = tk.Label(
            frame, text="Количество человек", anchor="w")
        self.people_count_var = tk.StringVar(frame)
        people_count_entry = tk.Entry(
            frame, textvariable=self.people_count_var)

        self.product_type_var.trace_add(
            "write", update_people_count_visibility)

        tk.Label(frame, text="Способ оплаты", anchor="w").grid(
            row=5, column=0, pady=10, sticky="w")
        self.split_payment_var = tk.BooleanVar(frame)
        tk.Checkbutton(frame, text="Раздельная оплата",
                       variable=self.split_payment_var).grid(row=5, column=1, pady=10)

        tk.Label(frame, text="Выберите дату", anchor="w").grid(
            row=3, column=0, pady=10, sticky="w")
        self.date_var = tk.StringVar(frame)

        # Year dropdown
        self.year_var = tk.StringVar(frame)
        self.year_var.set(str(self.today_date.year))  # Default to current year
        year_options = [str(year)
                        for year in range(self.today_date.year, 2027)]
        year_menu = tk.OptionMenu(frame, self.year_var, *year_options)
        year_menu.configure(width=dropdown_width)
        year_menu.grid(row=3, column=1, pady=10)

        # Month dropdown
        self.month_var = tk.StringVar(frame)
        # Define month_options before using it
        month_options = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        # Default to current month
        self.month_var.set(month_options[self.today_date.month - 1])
        # Time input
        self.time_var = tk.StringVar(frame)
        self.time_var.set("09:00")  # Default value

        tk.Label(frame, text="Введите время (чч:мм)").grid(
            row=2, column=4, pady=10)

        self.time_entry = tk.Entry(frame, textvariable=self.time_var)
        self.time_entry.grid(row=3, column=4, pady=10, padx=10)

        # Button to set today's date
        tk.Button(frame, text="Сегодня", command=self.set_today_date).grid(
            row=3, column=5, pady=10)

        # Button to set current time
        tk.Button(frame, text="Сейчас", command=self.set_current_time).grid(
            row=2, column=5, pady=10)

        month_menu = tk.OptionMenu(frame, self.month_var, *month_options)
        month_menu.configure(width=dropdown_width)
        month_menu.grid(row=3, column=2, pady=10)

        # Day dropdown
        self.day_var = tk.StringVar(frame)
        self.day_var.set(str(self.today_date.day))  # Default to current day
        day_options = [str(day) for day in range(1, 32)]
        day_menu = tk.OptionMenu(frame, self.day_var, *day_options)
        day_menu.configure(width=dropdown_width)
        day_menu.grid(row=3, column=3, pady=10, padx=10)

        self.actuallPayment = tk.IntVar(frame)
        self.actuallPayment.set(0)

        tk.Button(frame, text="Далее", command=lambda: self.show_frame(
            "summary_frame")).grid(row=11, column=5, pady=10)
        tk.Button(frame, text="Назад", command=lambda: self.show_frame("employee_frame")).grid(
            row=11, column=0, pady=10)

        def calculate_payment():
            total_price = 0
            try:
                # Получить дату и время из введенных значений
                selected_date = datetime.date(
                    int(self.year_var.get()),
                    # Индексация месяцев начинается с 0
                    month_options.index(self.month_var.get()) + 1,
                    int(self.day_var.get())
                )
                selected_time = datetime.datetime.strptime(
                    self.time_var.get(), "%H:%M").time()

                # Базовая цена для обычных игр
                if selected_date.weekday() >= 4:  # 5 и 6 соответствуют субботе и воскресенью, 4 — пятница
                    AWgame_price = 1800  # Увеличить базовую цену для выходных
                else:
                    if selected_time >= datetime.time(16, 0):
                        AWgame_price = 1600  # Увеличить базовую цену для вечерних часов
                    else:
                        AWgame_price = 1400  # Базовая цена для будних дней

                # Базовая цена для одиночных игр за 15 минут
                AloneGamePrice = 450

                if self.product_type_var.get() == "Время":
                    people_count = int(self.people_count_var.get(
                    )) if self.people_count_var.get().isdigit() else 1
                    hrsofplaytime = int(
                        self.product_var.get().split(" ")[0]) / 60
                    percentage = int(self.percentage_entry_var.get()) if self.payment_type_var.get() in [
                        "Доплата", "Предоплата"] and self.percentage_entry_var.get().isdigit() else 0

                    total_price = AWgame_price * people_count * hrsofplaytime
                    if percentage > 0:
                        total_price = total_price * (percentage / 100)

                elif self.product_type_var.get() == "Тариф":
                    self.product_var.get()

                    # Get selected date and time
                    selected_date = datetime.date(
                        int(self.year_var.get()),
                        month_options.index(self.month_var.get()),
                        int(self.day_var.get())
                    )

                    selected_time = datetime.datetime.strptime(
                        self.time_var.get(), "%H:%M").time()

                    # Check if the selected date is a weekend
                    # 5 and 6 correspond to Saturday and Sunday
                    is_weekend = selected_date.weekday() >= 4
                    print(selected_date.weekday())
                    is_evening = selected_time >= datetime.time(16, 0)

                    percentage = int(self.percentage_entry_var.get()) if self.payment_type_var.get() in [
                        "Доплата", "Предоплата"] and self.percentage_entry_var.get().isdigit() else 0
                    # Adjust price based on weekend, evening, and tariff
                    if self.product_var.get() == "STD":
                        total_price = 25000 if is_weekend else \
                            20000 if is_evening else 15000
                    elif self.product_var.get() == "HARD":
                        total_price = 35000 if is_weekend else \
                            27500 if is_evening else 20000
                    elif self.product_var.get() == "VIP":
                        total_price = 45000 if is_weekend else \
                            35000 if is_evening else 25000
                    if percentage > 0:
                        total_price = total_price * (percentage / 100)

                elif self.product_type_var.get() == "Одиночная игра":
                    self.product_var.get()
                    people_count = int(self.people_count_var.get(
                    )) if self.people_count_var.get().isdigit() else 1
                    percentage = int(self.percentage_entry_var.get()) if self.payment_type_var.get() in [
                        "Доплата", "Предоплата"] and self.percentage_entry_var.get().isdigit() else 0
                    hrsofplaytime = int(
                        self.product_var.get().split(" ")[0]) / 15
                    total_price = AloneGamePrice * people_count * hrsofplaytime
                    if percentage > 0:
                        total_price = total_price * (percentage / 100)

                elif self.product_type_var.get() == "Абонемент":
                    subscription_price = int(self.product_var.get().split(" ")[
                                             1])  # Extract price from string
                    percentage = int(self.percentage_entry_var.get()) if self.payment_type_var.get() in [
                        "Доплата", "Предоплата"] and self.percentage_entry_var.get().isdigit() else 0
                    total_price = subscription_price
                    if percentage > 0:
                        total_price = total_price * (percentage / 100)

                elif self.product_type_var.get() == "Сертификат":
                    certificate_price = int(self.product_var.get().split(" ")[
                                            1])  # Extract price from string
                    percentage = int(self.percentage_entry_var.get()) if self.payment_type_var.get() in [
                        "Доплата", "Предоплата"] and self.percentage_entry_var.get().isdigit() else 0
                    total_price = certificate_price
                    if percentage > 0:
                        total_price = total_price * (percentage / 100)
                self.actuallPayment.set(total_price)

                payLabel.config(
                    text=f"Рассчитанная \n стоимость: {self.actuallPayment.get()}")

            except ValueError as e:
                payLabel.config(text="Ошибка в расчетах")
                print(f"Error is {e}")

                def clear_label():
                    payLabel.config(text="")
                Timer(1.5, clear_label).start()

        tk.Button(frame, text="Рассчитать", command=calculate_payment).grid(
            row=1, column=5, pady=10)

        payLabel = tk.Label(
            frame, text=f"Рассчитанная \n стоимость: {self.actuallPayment.get()}", font=("Arial", 20))
        payLabel.grid(row=0, column=3, pady=10)

        # Define payment methods
        self.payment_methods = ["Наличные по кассе", "Карта", "QR/СБП", "Н/П"]
        self.payment_entries = []
        self.payment_dropdown_var = tk.StringVar(frame)
        self.payment_dropdown_var.set(self.payment_methods[0])  # Default value

        def update_payment_method_visibility(*args):
            if self.split_payment_var.get():  # If split payment is selected
                # Show multiple entry fields for payment methods
                for i, method in enumerate(self.payment_methods):
                    tk.Label(frame, text=f"{method}:", anchor="w").grid(
                        row=6 + i, column=0, pady=5, sticky="w")
                    payment_var = tk.StringVar(frame)
                    tk.Entry(frame, textvariable=payment_var).grid(
                        row=6 + i, column=1, pady=5)
                    self.payment_entries.append(payment_var)
                # Hide the dropdown
                payment_dropdown.grid_forget()
            else:  # If split payment is not selected
                # Hide multiple entry fields
                for widget in frame.grid_slaves():
                    if int(widget.grid_info()["row"]) >= 6 and not isinstance(widget, tk.Button):
                        widget.grid_forget()
                self.payment_entries.clear()
            # Show the dropdown
                payment_dropdown.grid(row=6, column=1, pady=5)

        # Dropdown for single payment method
        payment_dropdown = tk.OptionMenu(
            frame, self.payment_dropdown_var, *self.payment_methods)
        payment_dropdown.configure(width=13)
        payment_dropdown.grid(row=6, column=1, pady=5)
        # Trace the split payment checkbox to update visibility
        self.split_payment_var.trace_add(
            "write", update_payment_method_visibility)

        # Add percentage input for Доплата or Предоплата
        self.percentage_label = tk.Label(frame, text="Проценты")
        self.percentage_entry_var = tk.StringVar(frame)
        self.percentage_entry = tk.Entry(
            frame, textvariable=self.percentage_entry_var)

        def update_percentage_visibility(*args):
            if self.payment_type_var.get() in ["Доплата", "Предоплата"]:
                self.percentage_label.grid(row=2, column=2, pady=10)
                self.percentage_entry.grid(row=2, column=3, pady=10)

            else:
                self.percentage_label.grid_forget()
                self.percentage_entry.grid_forget()

        self.payment_type_var.trace_add("write", update_percentage_visibility)

        def update_date_visibility(*args):
            if self.product_type_var.get() in ["Сертификат", "Абонемент"]:
                year_menu.grid_forget()
                month_menu.grid_forget()
                day_menu.grid_forget()
                self.time_entry.grid_forget()
                self.time_var.set("")  # Clear time input
                self.date_var.set("")  # Clear date input
                self.time_var.set("00:00")  # Clear time input
                # Remove labels for date and time
                for widget in frame.grid_slaves():
                    if widget.cget("text") in ["Выберите дату", "Введите время (чч:мм)", "Сегодня", "Сейчас"]:
                        widget.grid_forget()
                self.date_var.set("")  # Clear date input
            else:
                self.time_entry.grid(row=3, column=4, pady=10, padx=10)
                tk.Label(frame, text="Выберите дату", anchor="w").grid(
                    row=3, column=0, pady=10, sticky="w")
                tk.Label(frame, text="Введите время (чч:мм)").grid(
                    row=2, column=4, pady=10)
                year_menu.grid(row=3, column=1, pady=10)
                month_menu.grid(row=3, column=2, pady=10)
                day_menu.grid(row=3, column=3, pady=10)
                # Add "Сегодня" and "Сейчас" buttons
                tk.Button(frame, text="Сегодня", command=self.set_today_date, fg="black", bg="black").grid(
                    row=3, column=5, pady=10)
                tk.Button(frame, text="Сейчас", command=self.set_current_time, fg="black", bg="black").grid(
                    row=2, column=5, pady=10)

        self.product_type_var.trace_add("write", update_date_visibility)

    def set_today_date(self):
        """Set the date inputs to today's date."""
        self.year_var.set(str(self.today_date.year))
        self.month_var.set(self.month_var.get())
        self.day_var.set(str(self.today_date.day))

    def set_current_time(self):
        """Set the time input to the current time."""
        current_time = datetime.datetime.now().strftime("%H:%M")
        self.time_var.set(current_time)

    def init_summary_frame(self):
        frame = tk.Frame(self.root, bg="black")
        self.frames["summary_frame"] = frame

        tk.Label(frame, text="Комментарий к продаже").grid(
            row=0, column=0, pady=10)
        self.comment_var = tk.StringVar(frame)
        tk.Entry(frame, textvariable=self.comment_var).grid(
            row=0, column=1, pady=10)

        tk.Button(frame, text="Отправить", command=self.submit_data).grid(
            row=1, column=2, columnspan=2, pady=10)
        tk.Button(frame, text="Назад", command=self.go_back).grid(
            row=1, column=0, pady=10)

    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.grid_forget()  # Скрыть все фреймы
        frame = self.frames[frame_name]
        frame.grid(row=0, column=0, padx=10, pady=10)  # Показать нужный фрейм
        frame.update_idletasks()  # Обновить интерфейс для плавного отображения

    def update_dropdown(self, *args):
        if self.product_type_var.get() == "Тариф":
            new_options = ["STD", "HARD", "VIP"]
        elif self.product_type_var.get() == "Время":
            new_options = [f"{i} мин" for i in range(30, 330, 30)]
        elif self.product_type_var.get() == "Одиночная игра":
            new_options = [f"{i} мин" for i in range(15, 325, 15)]
        elif self.product_type_var.get() == "Сертификат":
            new_options = [f"На {i} рублей" for i in [1000, 3000, 5000, 10000]]
        elif self.product_type_var.get() == "Абонемент":
            new_options = [f"За {i} рублей" for i in [2500, 4500, 6500]]
        menu = self.product_dropdown["menu"]
        menu.delete(0, "end")
        for option in new_options:
            menu.add_command(
                label=option, command=lambda value=option: self.product_var.set(value))
        self.product_var.set(new_options[0])

    def submit_data(self):
        self.data_summary = {
            "Тип товара": self.product_type_var.get(),
            "Товар": self.product_var.get(),
            "Стоимость": self.actuallPayment.get(),
            "Способ оплаты": self.payment_dropdown_var.get() if not self.split_payment_var.get() else "Раздельная",
            "Тип оплаты": self.payment_type_var.get(),
            "Количество человек": self.people_count_var.get(),
            "Дата": f"{self.day_var.get()} {self.month_var.get()} {self.year_var.get()}",
            "Время": self.time_var.get(),
            "Проценты": self.percentage_entry_var.get() if self.payment_type_var.get() in ["Доплата", "Предоплата"] else "100",
            "Время чека": self.comment_var.get()
        }
        print(self.data_summary)

        self.show_frame("payment_frame")

    def go_back(self):
        # Get the current frame
        current_frame = None
        for frame_name, frame in self.frames.items():
            if frame.winfo_ismapped():
                current_frame = frame_name
                break

        # Define the navigation order
        frame_order = ["login_frame", "employee_frame",
                       "payment_frame", "summary_frame"]

        # Find the previous frame in the order
        if current_frame:
            current_index = frame_order.index(current_frame)
            if current_index > 0:
                previous_frame = frame_order[current_index - 1]
                self.show_frame(previous_frame)

    def openUI(self, root):
        root.mainloop()
