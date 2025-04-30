import tkinter as tk
from threading import Timer
import hashlib
import datetime
import sys
from tkinter import messagebox
from tkinter import ttk
from Model.model import Model


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
        self.root.tk.call("tk", "scaling", 1.1)
        # Use macOS system font
        self.root.option_add("*Font", "San Francisco 14")
        # Flat buttons for macOS look
        self.root.option_add("*Button.relief", "flat")
        self.root.option_add("*Button.highlightThickness",
                             0)  # Remove button border
        self.use_item = False
        # Light gray button background
        self.root.option_add("*Button.background", "#E5E5E5")
        # Slightly darker gray for active buttons
        self.root.option_add("*Button.activeBackground", "#D4D4D4")
        # White text for buttons
        self.root.option_add("*Button.foreground", "#000000")
        # Light gray background for labels
        self.root.option_add("*Label.background", "#F9F9F9")
        # Black text for labels
        self.root.option_add("*Label.foreground", "#000000")
        # White background for entry fields
        self.root.option_add("*Entry.background", "#FFFFFF")
        # Black text for entry fields
        self.root.option_add("*Entry.foreground", "#000000")
        # Thin border for entry fields
        self.root.option_add("*Entry.highlightThickness", 1)
        # Rounded corners for buttons (macOS-like)
        self.root.option_add("*Button.borderRadius", 5)

        self.root.configure(bg="#F0F0F0")  # Set root background to light gray
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
        self.init_closeShift_frame()
        self.show_frame("employee_frame")
        self.wrongAttempts = 0
        # Define the navigation order
        self.frame_order = ["login_frame", "employee_frame",
                            "payment_frame", "summary_frame", "closeShift_frame"]

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
                    target_geometry = (1100, 650)
                elif frame_name == "employee_frame":
                    target_geometry = (660, 310)
                elif frame_name == "login_frame":
                    target_geometry = (300, 300)
                elif frame_name == "summary_frame":
                    target_geometry = (480, 180)
                elif frame_name == "closeShift_frame":
                    target_geometry = (1300, 500)
                if target_geometry:
                    current_geometry = self.root.geometry()
                    # Extract width and height, ignoring position offsets
                    current_width, current_height = map(
                        int, current_geometry.split("+")[0].split("x"))
                    target_width, target_height = target_geometry

                    # Fewer steps for quicker resizing
                    width_step = (target_width - current_width) / 50
                    height_step = (target_height - current_height) / 50

                    def animate_resize(step=0):
                        if step <= 50:  # Reduce total steps
                            new_width = int(current_width + width_step * step)
                            new_height = int(
                                current_height + height_step * step)
                            self.root.geometry(f"{new_width}x{new_height}")
                            # Slightly longer delay for smoother animation
                            self.root.after(5, animate_resize, step + 1)

                    animate_resize()

    def get_current_month_name(self):
        """Returns the Russian name of the current month."""
        months_in_russian = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        current_month = datetime.datetime.now().month
        return months_in_russian[current_month - 1]

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
                pass

        password_menu = tk.Menu(self.root, tearoff=0)
        password_menu.add_command(label="Paste", command=paste_password)

        def show_password_menu(event):
            password_menu.post(event.x_root, event.y_root)

        password_entry.bind("<Button-3>", show_password_menu)

        tk.Button(frame, text="Войти", command=self.validate_login, bg="white", fg="black").grid(
            row=3, column=0, columnspan=2, pady=10)

    def validate_login(self):
        """
        Validates the login credentials entered by the user.

        This method retrieves the username and password from the respective input fields,
        hashes the entered password using SHA-256, and compares the credentials with the
        predefined username and hashed password. If the credentials are correct, the user
        is redirected to the "employee_frame". Otherwise, an error message is displayed,
        and the number of remaining login attempts is shown. If the user exceeds the maximum
        number of allowed attempts (5), the application is closed.

        Error messages:
            - "Неверный логин и пароль" (Incorrect username and password)
            - "Неверный логин" (Incorrect username)
            - "Неверный пароль" (Incorrect password)

        Side effects:
            - Displays error messages on the login frame.
            - Tracks the number of incorrect login attempts.
            - Closes the application after 5 failed attempts.

        Attributes:
            username_var (tk.StringVar): Variable holding the entered username.
            password_var (tk.StringVar): Variable holding the entered password.
            frames (dict): Dictionary containing the application's frames.
            root (tk.Tk): The root Tkinter window.
            wrongAttempts (int): Counter for the number of failed login attempts.

        Predefined credentials:
            - Username: "spb-aw"
            - Password (hashed): "fc17f007ddcf314128317bbed059ae8b253176d0dd846243627492f215121a5c"
        """

        username = self.username_var.get()
        password = self.password_var.get()

        usernamer = "spb-aw"
        passwordr = "fc17f007ddcf314128317bbed059ae8b253176d0dd846243627492f215121a5c"

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

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
            attempts_left = 5 - self.wrongAttempts
            tk.Label(self.frames["login_frame"], text=f"Осталось попыток: {attempts_left}", fg="red").grid(
                row=5, column=0, columnspan=2, pady=5)
            if self.wrongAttempts == 5:
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
            row=0, column=1, pady=10)
        tk.Label(frame, text="Имя работника").grid(
            row=1, column=0, columnspan=1, pady=10)
        tk.Label(frame, text="Тип работника ").grid(
            row=1, column=1, columnspan=1, pady=10)
        tk.Label(frame, text="Тип смены").grid(
            row=1, column=2, columnspan=1, pady=10)
        self.employee_vars = []
        self.employee_menus = []
        dropdown_width = 18  # Set a consistent width for all dropdowns
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
                frame, self.workplace_var, "Июнь", "Пик", "Лондон Молл", "Коменда")
            workplace_menu.configure(width=dropdown_width)
            workplace_menu.grid(row=5, column=1, pady=10)

        tk.Button(frame, text="Далее", command=self.preview_employees, bg="white", fg="black").grid(
            row=6, column=1, pady=10)

    def preview_employees(self):
        """Preview the selected employees with the last item as 'Арена'."""
        employee_preview = []
        for i in range(3):
            employee_preview.append([
                self.employee_vars[i].get(),
                self.frames["employee_frame"].grid_slaves(
                    row=i + 2, column=1)[0].cget("text"),
                self.frames["employee_frame"].grid_slaves(
                    row=i + 2, column=2)[0].cget("text")
            ])
        employee_preview.append("На арене:")
        employee_preview.append(self.workplace_var.get())
        employee_preview = [
            item for item in employee_preview[:-1]
            if item[0] not in ["Пропуск", "Выберете работника"]
        ] + [employee_preview[-1]]

        preview_window = tk.Toplevel(self.root)
        preview_window.title("Предварительный просмотр сотрудников")
        preview_window.geometry("400x500")

        text_widget = tk.Text(preview_window, wrap="word",
                              font=("Helvetica", 12))
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        # Populate the text widget with the employee preview in a table-like format
        # Calculate column widths based on the longest text in each column
        col_widths = [max(len(str(employee[i])) for employee in employee_preview if isinstance(
            employee, list)) + 2 for i in range(3)]
        # Add a default width for the last "На арене" row
        col_widths.append(20)

        # Insert header row with dynamic column widths
        text_widget.insert(
            "end", f"{'Имя':<{col_widths[0]}}{'Тип':<{col_widths[1]}}{'Смена':<{col_widths[2]}}\n")
        text_widget.insert("end", "-" * sum(col_widths) + "\n")

        # Insert employee data rows
        for employee in employee_preview:
            if isinstance(employee, list):
                text_widget.insert(
                    "end", f"{employee[0]:<{col_widths[0]}}{employee[1]:<{col_widths[1]}}{employee[2]:<{col_widths[2]}}\n"
                )
            else:
                text_widget.insert(
                    "end", f"\n{employee.center(sum(col_widths))}\n")

        # Make the text widget read-only
        text_widget.config(state="disabled")
        button_frame = tk.Frame(preview_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Согласен", command=lambda: self.agreeToDisagree(
            True, preview_window=preview_window, next_frame="payment_frame", key="emp"), bg="white", fg="black").pack(side="left", padx=10)
        tk.Button(button_frame, text="Не согласен", command=lambda: self.agreeToDisagree(
            False, preview_window=preview_window, act_frame="employee_frame", key="emp"), bg="white", fg="black").pack(side="right", padx=10)

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
        dropdown_width = 18
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
        self.payment_type_var.set("Полная оплата")  # Default
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
            def fade_in(widget):
                widget.grid()  # Show the widget

            def fade_out(widget):
                widget.grid_forget()  # Hide the widget

            if self.product_type_var.get() in ["Время", "Одиночная игра"]:
                people_count_label.grid(row=4, column=0, pady=10, sticky="w")
                people_count_entry.grid(row=4, column=1, pady=10)
                fade_in(people_count_label)
                fade_in(people_count_entry)
            else:
                fade_out(people_count_label)
                fade_out(people_count_entry)

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
        self.use_abo_cert_var = tk.BooleanVar(frame)
        tk.Checkbutton(frame, text="Раздельная оплата",
                       variable=self.split_payment_var).grid(row=5, column=1, pady=10)

        useABOcERT = tk.Checkbutton(
            frame, text=f"", variable=self.use_abo_cert_var)
        useABOcERT.grid(row=0, column=2)
        useABOcERT.grid_forget()

        def update_use_abo_cert_visibility(*args):
            if self.product_type_var.get() in ["Абонемент", "Сертификат"]:
                useABOcERT.grid(padx=10, row=0, column=2)
                useABOcERT.config(
                    text=f"Использовать \n{self.product_type_var.get()}?")
            else:
                useABOcERT.grid_forget()

        def update_use_var(*args):
            if self.use_abo_cert_var.get():
                self.use_item = True
            else:
                self.use_item = False

        self.use_abo_cert_var.trace_add("write", update_use_var)

        self.product_type_var.trace_add(
            "write", update_use_abo_cert_visibility)
        tk.Label(frame, text="Выберите дату", anchor="w").grid(
            row=3, column=3, pady=10, sticky="w")
        self.date_var = tk.StringVar(frame)

        # Year dropdown
        self.year_var = tk.StringVar(frame)
        self.year_var.set(str(self.today_date.year))  # Default to current year
        year_options = [str(year)
                        for year in range(self.today_date.year, 2027)]
        year_menu = tk.OptionMenu(frame, self.year_var, *year_options)
        year_menu.configure(width=dropdown_width)
        year_menu.grid(row=4, column=3, pady=10)

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
        self.time_var.set("10:00")  # Default value

        tk.Label(frame, text="Введите время (чч:мм)").grid(
            row=3, column=4, pady=10)

        self.time_entry = tk.Entry(frame, textvariable=self.time_var)
        self.time_entry.grid(row=4, column=4, pady=10, padx=10)

        # Button to set today's date
        tk.Button(frame, text="Сегодня", command=self.set_today_date, bg="white", fg="black").grid(
            row=4, column=5, pady=10)

        # Button to set current time
        tk.Button(frame, text="Сейчас", command=self.set_current_time, bg="white", fg="black").grid(
            row=3, column=5, pady=10)

        month_menu = tk.OptionMenu(frame, self.month_var, *month_options)
        month_menu.configure(width=dropdown_width)
        month_menu.grid(row=5, column=3, pady=10)

        # Day dropdown
        self.day_var = tk.StringVar(frame)
        self.day_var.set(str(self.today_date.day))  # Default to current day
        day_options = [str(day) for day in range(1, 32)]
        day_menu = tk.OptionMenu(frame, self.day_var, *day_options)
        day_menu.configure(width=dropdown_width)
        day_menu.grid(row=6, column=3, pady=10, padx=10)

        self.actuallPayment = tk.IntVar(frame)
        self.actuallPayment.set(0)
        self.error_label = tk.Label(
            frame, text="", fg="red")
        self.error_label.grid(row=12, column=0,
                              columnspan=2, pady=5)

        tk.Button(frame, text="Далее", command=lambda: self.show_frame(
            "summary_frame"), bg="white", fg="black").grid(row=11, column=5, pady=10)

        tk.Button(frame, text="Назад", command=lambda: self.show_frame("employee_frame"), bg="white", fg="black").grid(
            row=11, column=0, pady=10)

        tk.Button(frame, text="Рассчитать", command=lambda: Model.calculate_payment(month_options, self.year_var, self.month_var, self.day_var, self.time_var, self.product_type_var, self.product_var, self.people_count_var, self.percentage_entry_var, self.payment_type_var, self.actuallPayment, payLabel), bg="white", fg="black").grid(
            row=1, column=5, pady=10)

        payLabel = tk.Label(
            frame, text=f"Рассчитанная \n стоимость: {self.actuallPayment.get()}", font=("Arial", 20),
            bg="black", relief="solid", borderwidth=2)
        payLabel.grid(row=0, column=3, pady=10)

        # Define payment methods
        self.payment_methods = ["Наличные по кассе", "Карта", "QR/СБП", "Н/П"]
        self.payment_entries = []
        self.payment_dropdown_var = tk.StringVar(frame)
        self.payment_dropdown_var.set(self.payment_methods[0])  # Default value
        # Dropdown for single payment method
        payment_dropdown = tk.OptionMenu(
            frame, self.payment_dropdown_var, *self.payment_methods)
        payment_dropdown.configure(width=dropdown_width)
        payment_dropdown.grid(row=6, column=1, pady=5)

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
                    if int(widget.grid_info()["row"]) >= 6 and (widget.grid_info()["column"] == 1 or widget.grid_info()["column"] == 0) and not isinstance(widget, tk.Button):
                        widget.grid_forget()
                self.payment_entries.clear()
            # Show the dropdown
                payment_dropdown.grid(row=6, column=1, pady=5)
                self.payment_dropdown_var.set(self.payment_methods[0])

        # Trace the split payment checkbox to update visibility
        self.split_payment_var.trace_add(
            "write", update_payment_method_visibility)

        tk.Button(frame, text="Закрытие смены", command=self.open_CSF, bg="white", fg="black").grid(
            row=11, column=4, pady=10)
        # Add percentage input for Доплата or Предоплата
        self.percentage_label = tk.Label(frame, text="Проценты")
        self.percentage_entry_var = tk.StringVar(frame)
        self.percentage_entry = tk.Entry(
            frame, textvariable=self.percentage_entry_var)

        def calculate_remaining_balance():
            try:
                # Calculate the total entered amount
                total_entered = sum(
                    int(entry.get()) for entry in self.payment_entries if entry.get().isdigit()
                )
                # Calculate the remaining balance
                remaining_balance = self.actuallPayment.get() - total_entered

                if any(entry.get().isdigit() for entry in self.payment_entries):
                    if remaining_balance < 0:
                        self.error_label.config(text="")
                        for i, entry_var in enumerate(self.payment_entries):
                            entry_widget = frame.grid_slaves(
                                row=6 + i, column=1)[0]
                            entry_widget.configure(bg="red", fg="white")
                        self.error_label.config(
                            text="Сумма превышает рассчитанную стоимость!", fg="red"
                        )
                    elif remaining_balance != 0:
                        self.error_label.config(text="")
                        for i, entry_var in enumerate(self.payment_entries):
                            entry_widget = frame.grid_slaves(
                                row=6 + i, column=1)[0]
                            entry_widget.config(bg="white", fg="black")
                        self.error_label.config(
                            text=f"Остаток: {remaining_balance}", fg="red"
                        )
                        self.root.after(
                            2000,
                            lambda: [
                                frame.grid_slaves(row=6 + j, column=1)[0].configure(
                                    bg="white", fg="black"
                                )
                                for j in range(len(self.payment_entries))
                            ],
                        )
                    else:
                        self.error_label.config(text="")
                        for i, entry_var in enumerate(self.payment_entries):
                            entry_widget = frame.grid_slaves(
                                row=6 + i, column=1)[0]
                            entry_widget.configure(bg="white", fg="black")
                        self.error_label.config(
                            text="Оплата успешно рассчитана!", fg="green"
                        )
                else:
                    self.error_label.config(text="")
                    self.error_label.config(
                        text="Нет введенных данных для проверки остатка.", fg="yellow")
            except ValueError as e:
                self.error_label.config(text="")
                self.error_label.config(text=f"Ошибка: {e}", fg="red")

        tk.Button(frame, text="Проверить остаток", command=calculate_remaining_balance, bg="white", fg="black").grid(
            row=11, column=3, pady=10
        )

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
                self.time_var.set("10:00")  # Clear time input
                # Remove labels for date and time
                for widget in frame.grid_slaves():
                    if widget.cget("text") in ["Выберите дату", "Введите время (чч:мм)", "Сегодня", "Сейчас"]:
                        widget.grid_forget()
                self.date_var.set("")  # Clear date input
            else:
                self.time_entry.grid(row=4, column=4, pady=10, padx=10)
                tk.Label(frame, text="Выберите дату", anchor="w").grid(
                    row=3, column=3, pady=10, sticky="w")
                tk.Label(frame, text="Введите время (чч:мм)").grid(
                    row=3, column=4, pady=10)
                year_menu.grid(row=4, column=3, pady=10)
                month_menu.grid(row=5, column=3, pady=10)
                day_menu.grid(row=6, column=3, pady=10)
                # Add "Сегодня" and "Сейчас" buttons
                tk.Button(frame, text="Сегодня", command=self.set_today_date,  bg="white", fg="black").grid(
                    row=4, column=5, pady=10)
                tk.Button(frame, text="Сейчас", command=self.set_current_time,  bg="white", fg="black").grid(
                    row=3, column=5, pady=10)

        self.product_type_var.trace_add("write", update_date_visibility)

    def set_today_date(self):
        """Set the date inputs to today's date."""
        self.year_var.set(str(self.today_date.year))
        self.month_var.set(str(self.get_current_month_name()))
        self.day_var.set(str(self.today_date.day))

    def set_current_time(self):
        """Set the time input to the current time."""
        current_time = datetime.datetime.now().strftime("%H:%M")
        self.time_var.set(current_time)

    def init_summary_frame(self):
        frame = tk.Frame(self.root, bg="black")
        self.frames["summary_frame"] = frame

        tk.Label(frame, text="Укажите время чека:").grid(
            row=0, column=0, pady=10)
        self.check_time = tk.StringVar(frame)
        tk.Entry(frame, textvariable=self.check_time).grid(
            row=0, column=1, pady=10)

        tk.Label(frame, text="Комментарий:").grid(
            row=1, column=0, pady=10)
        self.comment_var = tk.StringVar(frame)
        tk.Entry(frame, textvariable=self.comment_var).grid(
            row=1, column=1, pady=10)

        tk.Button(frame, text="Отправить", bg="white", fg="black", command=self.make_data).grid(
            row=2, column=2, columnspan=2, pady=10)
        tk.Button(frame, text="Назад", bg="white", fg="black", command=self.go_back).grid(
            row=2, column=0, pady=10)

    def init_closeShift_frame(self):
        frame = tk.Frame(self.root, bg="black")
        self.frames["closeShift_frame"] = frame

        tk.Label(frame, text="Закрытие смены", font=("Helvetica", 16), bg="black", fg="white").grid(
            row=0, column=0, columnspan=2, pady=10)

        # Create a treeview widget to display all requests
        self.requests_tree = tk.ttk.Treeview(frame, columns=(
            "Тип товара, Товар", "Время чека", "Количество человек", "Карта",
            "QR/СБП", "Наличные по кассе", "НП", "Игра AW",
            "Дата игры", "Время"
        ), show="headings", height=15)

        # Define column headings and widths
        for col in self.requests_tree["columns"]:
            self.requests_tree.heading(col, text=col)
            self.requests_tree.column(col, width=120, anchor="center")

        self.requests_tree.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10)

        # Populate the treeview with all made requests
        self.update_requests_tree()

        # Buttons for actions
        tk.Button(frame, text="Открыть предпросмотр отчета", command=self.close_shift, bg="white", fg="black").grid(
            row=2, column=0, pady=10)
        tk.Button(frame, text="Назад", command=lambda: self.show_frame("summary_frame"), bg="white", fg="black").grid(
            row=2, column=1, pady=10)

    def update_requests_tree(self):
        """
        Update the treeview widget with all made requests.

        This method clears the existing rows in the `requests_tree` widget and 
        populates it with data from `self.updater.all_requests`. If there are no 
        requests available, a placeholder row with "Нет данных" is added.

        The data displayed in the treeview includes:
        - Тип товара and Товар (combined into a single string)
        - Время чека
        - Количество человек
        - Карта
        - QR/СБП
        - Наличные по кассе
        - НП
        - Игра AW
        - Дата игры
        - Время
        """
        """Update the treeview widget with all made requests."""
        # Clear the treeview
        for item in self.requests_tree.get_children():
            self.requests_tree.delete(item)

        if not self.updater.all_requests.empty:
            # Populate the treeview rows
            for _, request in self.updater.all_requests.iterrows():
                self.requests_tree.insert("", "end", values=(
                    str(request["Тип товара"]+" " +
                        request["Товар"]), request["Время чека"],
                    request["Количество человек"], request["Карта"], request["QR/СБП"],
                    request["Наличные по кассе"], request["НП"], request["Игра AW"],
                    request["Дата игры"], request["Время"]
                ))
        else:
            # Add a placeholder row if there are no requests
            self.requests_tree.insert("", "end", values=(
                "Нет данных",) * len(self.requests_tree["columns"]))

    def open_CSF(self):
        self.update_requests_tree()
        self.show_frame("closeShift_frame")

    def close_shift(self):
        """Handle the close shift action."""
        if tk.messagebox.askyesno("Подтверждение", "Вы уверены, что хотите закрыть смену?"):
            # Perform any necessary cleanup or final actions
            tk.messagebox.showinfo("Закрытие смены", "Смена успешно закрыта!")
            self.on_close()

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

    def show_preview(self):
        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("Предварительный просмотр")
        self.preview_window.geometry("600x500")

        text_widget = tk.Text(self.preview_window, wrap="word",
                              font=("Helvetica", 12))
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        # Populate the text widget with the data summary
        for key, value in self.data_summary.items():
            text_widget.insert("end", f"{key}: {value}\n")

        # Make the text widget read-only
        text_widget.config(state="disabled")
        self.isAgreed = False
        button_frame = tk.Frame(self.preview_window)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Согласен",
                  command=lambda: self.agreeToDisagree(True, self.preview_window, next_frame="payment_frame"), bg="white", fg="black").pack(side="left", padx=10)
        tk.Button(button_frame, text="Не согласен",
                  command=lambda: self.agreeToDisagree(False, self.preview_window, next_frame="payment_frame"), bg="white", fg="black").pack(side="right", padx=10)

    def agreeToDisagree(self, isAgreed, preview_window, act_frame="payment_frame", next_frame="summary_frame", key="sell"):
        """
        Handles the user's agreement or disagreement to proceed with a specific action.

            Args:
                isAgreed (bool): Indicates whether the user agrees (True) or disagrees (False).
                preview_window (tk.Toplevel): The preview window that will be destroyed after the action.
                act_frame (str, optional): The name of the current active frame to return to if the user disagrees. Defaults to "payment_frame".
                next_frame (str, optional): The name of the next frame to navigate to if the user agrees. Defaults to "summary_frame".
                key (str, optional): "sell" triggers a sell request, while "emp" triggers an employee request. Defaults to "sell".
            Behavior:
                - If `isAgreed` is True:
                    - Executes the appropriate action based on the `key` parameter.
                    - Displays a success message indicating the request has been sent.
                    - Navigates to the `next_frame`.
                    - Closes the `preview_window`.
                - If `isAgreed` is False:
                    - Displays a message prompting the user to review and resend the request.
                    - Navigates back to the `act_frame`.
                    - Closes the `preview_window`.
        """

        if isAgreed:
            if key == "sell":
                self.updater.catch_req_sell(self.data_summary)
            elif key == "emp":
                self.get_employee_request()
            tk.messagebox.showinfo(
                "Внимание!", "Запрос отправлен в таблицу!")
            self.show_frame(next_frame)
            preview_window.destroy()
        else:
            tk.messagebox.showinfo(
                "Внимание!", "Уточните детали и отправьте запрос еще раз!")
            self.show_frame(act_frame)
            preview_window.destroy()

    def make_data(self):

        self.data_summary = {
            "Тип товара": self.product_type_var.get(),
            "Товар": self.product_var.get(),
            "Стоимость": self.actuallPayment.get(),
            "Способ оплаты": self.payment_dropdown_var.get() if not self.split_payment_var.get() else "Раздельная",
            "Тип оплаты": self.payment_type_var.get(),
            "Количество человек": 8 if self.product_type_var.get() in ["Тариф"] and self.product_var.get() in ["STD"] else 12 if self.product_type_var.get() in ["Тариф"] and self.product_var.get() in ["HARD"] else 16 if self.product_type_var.get() in ["Тариф"] and self.product_var.get() in ["VIP"] else int(self.people_count_var.get()) if self.people_count_var.get().isdigit() else 0,
            "Дата": f"{self.day_var.get()} {self.month_var.get()} {self.year_var.get()}",
            "Время": self.time_var.get(),
            "Проценты": self.percentage_entry_var.get() if self.payment_type_var.get() in ["Доплата", "Предоплата"] else "100",
            "Время чека": self.check_time.get(),
            "Комментарий": self.comment_var.get(),
            "НП": self.payment_entries[self.payment_methods.index("Н/П")].get() if self.split_payment_var.get() and self.payment_entries and self.payment_entries[self.payment_methods.index("Н/П")].get().isdigit() else (self.actuallPayment.get() if not self.split_payment_var.get() and self.payment_dropdown_var.get() == "Н/П" else 0),
            "Наличные по кассе": self.payment_entries[self.payment_methods.index("Наличные по кассе")].get() if self.split_payment_var.get() and self.payment_entries and self.payment_entries[self.payment_methods.index("Наличные по кассе")].get().isdigit() else (self.actuallPayment.get() if not self.split_payment_var.get() and self.payment_dropdown_var.get() == "Наличные по кассе" else 0),
            "Карта": self.payment_entries[self.payment_methods.index("Карта")].get() if self.split_payment_var.get() and self.payment_entries and self.payment_entries[self.payment_methods.index("Карта")].get().isdigit() else (self.actuallPayment.get() if not self.split_payment_var.get() and self.payment_dropdown_var.get() == "Карта" else 0),
            "QR/СБП": self.payment_entries[self.payment_methods.index("QR/СБП")].get() if self.split_payment_var.get() and self.payment_entries and self.payment_entries[self.payment_methods.index("QR/СБП")].get().isdigit() else (self.actuallPayment.get() if not self.split_payment_var.get() and self.payment_dropdown_var.get() == "QR/СБП" else 0),
            "Игра AW": 0 if self.payment_type_var.get() == "Предоплата" or self.product_type_var.get() in ["Абонемент", "Сертификат"] and not self.use_abo_cert_var.get() else (
                self.actuallPayment.get() * (100 / int(self.percentage_entry_var.get())) if self.payment_type_var.get(
                ) == "Доплата" and self.percentage_entry_var.get().isdigit() and not self.use_abo_cert_var.get() else self.actuallPayment.get()
            )
        }

        self.show_preview()

    def go_back(self):
        # Get the current frame
        current_frame = None
        for frame_name, frame in self.frames.items():
            if frame.winfo_ismapped():
                current_frame = frame_name
                break

        # Find the previous frame in the order
        if current_frame:
            current_index = self.frame_order.index(current_frame)
            if current_index > 0:
                previous_frame = self.frame_order[current_index - 1]
                self.show_frame(previous_frame)

    def openUI(self, root):
        root.mainloop()
