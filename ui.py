import tkinter as tk
import datetime
from FFCWP import ffcwp
import os
from dotenv import load_dotenv
import hashlib

class UIManager:
    def __init__(self, root, sheetwages, employees):
        employees.append("Пропуск")
        self.sheetwages = sheetwages
        self.employees = employees
        self.root = root
        self.root.title("Управление продажами")
        self.frames = {}
        self.today_date = datetime.date.today()
        # Initialize frames
        self.init_login_frame()
        self.init_employee_frame()
        self.init_payment_frame()
        self.init_summary_frame()
        self.show_frame("employee_frame")
        self.wrongAttempts = 0

    def enforce_frame_size(self, event):
        for frame_name, frame in self.frames.items():
            if frame.winfo_ismapped():
                if frame_name == "payment_frame":
                    self.root.geometry("460x500")
                elif frame_name == "employee_frame":
                    self.root.geometry("460x300")
                elif frame_name == "login_frame":
                    self.root.geometry("200x200")
                elif frame_name == "summary_frame":
                    self.root.geometry("300x200")
            
    def init_login_frame(self):
        self.root.geometry("200x200")
        frame = tk.Frame(self.root)
        self.frames["login_frame"] = frame

        tk.Label(frame, text="Введите логин и пароль").grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(frame, text="Логин").grid(row=1, column=0, pady=5)
        self.username_var = tk.StringVar(frame)
        tk.Entry(frame, textvariable=self.username_var).grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Пароль").grid(row=2, column=0, pady=5)
        self.password_var = tk.StringVar(frame)
        password_entry = tk.Entry(frame, textvariable=self.password_var, show="*")
        password_entry.grid(row=2, column=1, pady=5)

        # Add a context menu for paste option
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

        tk.Button(frame, text="Войти", command=self.validate_login).grid(row=3, column=0, columnspan=2, pady=10)

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
            error_message = tk.Label(self.frames["login_frame"], text=error_text, fg="red")
            error_message.grid(row=4, column=0, columnspan=2, pady=5)
            self.root.after(1500, error_message.destroy)
            self.wrongAttempts += 1
            attempts_left = 3 - self.wrongAttempts
            tk.Label(self.frames["login_frame"], text=f"Осталось попыток: {attempts_left}", fg="red").grid(row=5, column=0, columnspan=2, pady=5)
            if self.wrongAttempts == 3:
                exit(0)

    def init_employee_frame(self):
        self.root.geometry("460x300")
        frame = tk.Frame(self.root)
        self.frames["employee_frame"] = frame

        tk.Label(frame, text="Окно выбор сотрудника").grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(frame, text="Работник").grid(row=1, column=0, columnspan=1, pady=10)
        tk.Label(frame, text="Тип работника ").grid(row=1, column=1, columnspan=1, pady=10)
        tk.Label(frame, text="Тип смены").grid(row=1, column=2, columnspan=1, pady=10)

        self.employee_vars = []
        self.employee_menus = []
        for i in range(3):
            employee_var = tk.StringVar(frame)
            employee_var.set("Выберете работника")  # Default value
            employee_var.trace_add("write", lambda *args, idx=i: self.update_employee_options(idx))
            self.employee_vars.append(employee_var)

            role_var = tk.StringVar(frame)
            role_var.set("Оператор")

            shift_var = tk.StringVar(frame)
            shift_var.set("1.0")

            employee_menu = tk.OptionMenu(frame, employee_var, *self.employees)
            employee_menu.grid(row=i + 2, column=0, padx=10, pady=5)
            self.employee_menus.append(employee_menu)

            tk.OptionMenu(frame, role_var, "Оператор", "Администратор", "Стажер").grid(row=i + 2, column=1, padx=10, pady=5)
            tk.OptionMenu(frame, shift_var, *[f"{i/10}" for i in range(1, 11)]).grid(row=i + 2, column=2, padx=10, pady=5)

        tk.Label(frame, text="Рабочее место").grid(row=5, column=0, pady=10)
        self.workplace_var = tk.StringVar(frame)
        self.workplace_var.set("Июнь")  # Default value
        tk.OptionMenu(frame, self.workplace_var, "Июнь", "Пик", "Лондон Молл").grid(row=5, column=1, pady=10)

        tk.Button(frame, text="Далее", command=lambda: self.get_employee_data()).grid(row=6, column=0, columnspan=2, pady=10)
                  
    def get_employee_data(self):
        """Формирует список данных сотрудников."""
        employee_data = []
        for i in range(3):
            employee_data.append([
                self.employee_vars[i].get(),
                self.frames["employee_frame"].grid_slaves(row=i + 2, column=1)[0].cget("text"),
                self.frames["employee_frame"].grid_slaves(row=i + 2, column=2)[0].cget("text")
            ])
        employee_data.append(self.workplace_var.get())
        print(employee_data)
        self.show_frame("payment_frame")
        return employee_data

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
        self.root.geometry("460x500")
        self.root.bind("<Configure>", self.enforce_frame_size)

        frame = tk.Frame(self.root)
        self.frames["payment_frame"] = frame

        tk.Label(frame, text="Выберите тип оплаты").grid(row=2, column=0, pady=10)
        self.payment_type_var = tk.StringVar(frame)
        self.payment_type_var.set("Тип оплаты")  # Default value
        tk.OptionMenu(frame, self.payment_type_var, "Доплата", "Предоплата", "Полная оплата").grid(row=2, column=1, pady=10)

        tk.Label(frame, text="Выберете Тип товара").grid(row=0, column=0, pady=10)
        self.product_type_var = tk.StringVar(frame)
        self.product_type_var.set("Тип товара")  # Default value
        tk.OptionMenu(frame, self.product_type_var, "Тариф", "Время", "Одиночная игра", "Абонемент", "Сертификат").grid(row=0, column=1, pady=10)

        self.product_var = tk.StringVar(frame)
        self.product_dropdown = tk.OptionMenu(frame, self.product_var, "")
        self.product_dropdown.grid(row=1, column=1, pady=10)

        self.product_type_var.trace_add("write", self.update_dropdown)

        tk.Label(frame, text="Количество человек").grid(row=4, column=0, pady=10)
        self.people_count_var = tk.StringVar(frame)
        tk.Entry(frame, textvariable=self.people_count_var).grid(row=4, column=1, pady=10)

        tk.Label(frame, text="Способ оплаты").grid(row=5, column=0, pady=10)
        self.split_payment_var = tk.BooleanVar(frame)
        tk.Checkbutton(frame, text="Раздельная оплата", variable=self.split_payment_var).grid(row=5, column=1, pady=10)


        self.payment_entries = []
        for i in range(3):
            tk.Label(frame, text=f"Способ {i + 1}").grid(row=6 + i, column=0, pady=5)
            payment_var = tk.StringVar(frame)
            tk.Entry(frame, textvariable=payment_var).grid(row=6 + i, column=1, pady=5)
            self.payment_entries.append(payment_var)

        # Add percentage input for Доплата or Предоплата
        self.percentage_label = tk.Label(frame, text="Проценты")
        self.percentage_entry_var = tk.StringVar(frame)
        self.percentage_entry = tk.Entry(frame, textvariable=self.percentage_entry_var)

        def update_percentage_visibility(*args):
            if self.payment_type_var.get() in ["Доплата", "Предоплата"]:
                self.percentage_label.grid(row=2, column=2, pady=10)
                self.percentage_entry.grid(row=2, column=3, pady=10)
            else:
                self.percentage_label.grid_forget()
                self.percentage_entry.grid_forget()

        self.payment_type_var.trace_add("write", update_percentage_visibility)

        tk.Button(frame, text="Далее", command=lambda: self.show_frame("summary_frame")).grid(row=9, column=0, columnspan=2, pady=10)

    def check_payment_type(self):
        if self.payment_type_var.get() in ["Доплата", "Предоплата"]:
            print(f"Selected payment type: {self.payment_type_var.get()}")
        else:
            print("Selected payment type is not Доплата or Предоплата")

    def init_summary_frame(self):
        frame = tk.Frame(self.root)
        self.frames["summary_frame"] = frame

        tk.Label(frame, text="Комментарий к продаже").grid(row=0, column=0, pady=10)
        self.comment_var = tk.StringVar(frame)
        tk.Entry(frame, textvariable=self.comment_var).grid(row=0, column=1, pady=10)

        tk.Button(frame, text="Отправить", command=self.submit_data).grid(row=1, column=0, columnspan=2, pady=10)

    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.grid_remove()  # Скрыть все фреймы
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
            menu.add_command(label=option, command=lambda value=option: self.product_var.set(value))
        self.product_var.set(new_options[0])

    def submit_data(self):
        print("Комментарий:", self.comment_var.get())
        print("Тип товара:", self.product_type_var.get())
        print("Товар:", self.product_var.get())
        print("Тип оплаты:", self.payment_type_var.get())
        print("Количество человек:", self.people_count_var.get())
        print("Способ оплаты:", "Раздельная" if self.split_payment_var.get() else "Обычная")
        for i, payment_var in enumerate(self.payment_entries):
            print(f"Способ {i + 1}:", payment_var.get())
        if self.payment_type_var.get() in ["Доплата", "Предоплата"]:
            print("Проценты:", self.percentage_entry_var.get())
        self.show_frame("payment_frame")

    def openUI(self, root):
        root.mainloop()

    def getCellAddrToday(self, sheetwages):
        addr = ffcwp.find_first_matching_cell(sheetwages, [self.today_date])
        return addr
