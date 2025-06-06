import tkinter as tk
from threading import Timer
import hashlib
import datetime
import sys
import socket
import uuid
from tkinter import messagebox
from tkinter import ttk
from Model.model import Model


class UIManager:
    """
    UIManager is a singleton class responsible for managing the graphical user interface (GUI) of the SellerForEmployees application.
    This class orchestrates the creation, configuration, and navigation of multiple frames (views) within a Tkinter-based desktop application. It handles user authentication, employee selection, payment processing, summary display, and shift closure, providing a cohesive workflow for the application's users.

        Args:
            _instance (UIManager): Singleton instance of the class.
            updater: External updater object for data operations.
            sheetwages: Reference to wage sheet or data source.
            employees (list): List of employee names for selection.
            root (tk.Tk): Main Tkinter root window.
            frames (dict): Dictionary mapping frame names to Tkinter Frame objects.
            today_date (datetime.date): Current date.
            address: Address or location information.
            employee_request: Stores selected employee data.
            wrongAttempts (int): Counter for failed login attempts.
            frame_order (list): Ordered list of frame names for navigation.
            Various Tkinter variables for UI state (e.g., StringVar, IntVar, BooleanVar).
        ------------------------------------------------------
        Methods:
            __new__(cls, *args, **kwargs): Ensures singleton instantiation.
            __init__(self, config): Initializes UIManager with configuration.
            on_close(self): Handles application shutdown.
            enforce_frame_size(self, event): Triggers animated resizing of frames.
            _apply_frame_size(self): Applies animated resizing to the current frame.
            get_current_month_name(self): Returns the current month name in Russian.
            init_login_frame(self): Sets up the login frame UI.
            validate_login(self): Validates user credentials and access.
            init_employee_frame(self): Sets up the employee selection frame.
            preview_employees(self): Shows a preview dialog for selected employees.
            get_employee_request(self): Collects and processes employee selection data.
            update_employee_options(self, changed_index): Updates dropdowns to prevent duplicate employee selection.
            init_payment_frame(self): Sets up the payment processing frame.
            set_today_date(self): Sets date fields to today's date.
            set_current_time(self): Sets time field to current time.
            init_summary_frame(self): Sets up the summary frame for final review.
            init_closeShift_frame(self): Sets up the shift closure frame.
            update_requests_tree(self): Updates the shift closure request table.
            open_CSF(self): Opens the close shift frame.
            close_shift(self): Handles shift closure logic and confirmation.
            show_frame(self, frame_name): Switches the visible frame.
            update_dropdown(self, *args): Updates product dropdown options based on selection.
            show_preview(self): Displays a summary preview dialog.
            agreeToDisagree(self, isAgreed, preview_window, ...): Handles user confirmation dialogs.
            make_data(self): Collects and summarizes all form data for processing.
            go_back(self): Navigates to the previous frame.
            openUI(self, root): Starts the Tkinter main loop.
        Usage:
            Instantiate UIManager with a configuration dictionary containing references to the Tkinter root, updater, employee list, and other dependencies. Call openUI(root) to start the application.
        Note:
            This class assumes the existence of external classes and modules such as Model, Updater, and various Tkinter widgets.
        """

    _instance = None
    def __new__(cls, *args, **kwargs):
        """
        Creates and returns a singleton instance of the UIManager class.
        This method overrides the default __new__ method to ensure that only one instance
        of the UIManager class is created (singleton pattern). If an instance already exists,
        it returns the existing instance; otherwise, it creates a new one.
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        Returns:
            UIManager: The singleton instance of the UIManager class.
        """

        if cls._instance is None:
            cls._instance = super(UIManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, config):
        root = config['root']
        sheetwages = config['sheetWAGES']
        employees = config.get('employees', [])
        self.updater = config['Updater']
        employees.append("Пропуск")
        self.resize_timer = None
        self.sheetwages = sheetwages
        self.employees = config['list_employee']
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.tk.call("tk", "scaling", 1.1)
        self.root.option_add("*Font", "San Francisco 14")
        self.root.option_add("*Button.relief", "flat")
        self.root.option_add("*Button.highlightThickness", 0)
        self.use_item = False
        self.root.option_add("*Button.background", "#E5E5E5")
        self.root.option_add("*Button.activeBackground", "#D4D4D4")
        self.root.option_add("*Button.foreground", "#000000")
        self.root.option_add("*Label.background", "#F9F9F9")
        self.root.option_add("*Label.foreground", "#000000")
        self.root.option_add("*Entry.background", "#FFFFFF")
        self.root.option_add("*Entry.foreground", "#000000")
        self.root.option_add("*Entry.highlightThickness", 1)
        self.root.option_add("*Button.borderRadius", 5)

        self.root.configure(bg="#F0F0F0")
        self.root.title("Заполнение отчета")
        self.frames = {}
        self.today_date = datetime.date.today()
        self.address = None
        self.employee_request = None
        self.init_login_frame()
        self.init_employee_frame()
        self.init_payment_frame()
        self.init_summary_frame()
        self.init_closeShift_frame()
        self.show_frame("login_frame")
        self.wrongAttempts = 0
        self.frame_order = ["login_frame", "employee_frame",
                            "payment_frame", "summary_frame", "closeShift_frame"]

    def on_close(self):
        if self.resize_timer:
            self.resize_timer.cancel()
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

    def enforce_frame_size(self, event):
        if self.resize_timer:
            self.resize_timer.cancel()
        self.resize_timer = Timer(0.1, self._apply_frame_size)
        self.resize_timer.start()

    def _apply_frame_size(self):
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
                    current_width, current_height = map(
                        int, current_geometry.split("+")[0].split("x"))
                    target_width, target_height = target_geometry
                    width_step = (target_width - current_width) / 50
                    height_step = (target_height - current_height) / 50

                    def animate_resize(step=0):
                        if step <= 50:
                            new_width = int(current_width + width_step * step)
                            new_height = int(
                                current_height + height_step * step)
                            self.root.geometry(f"{new_width}x{new_height}")
                            self.root.after(5, animate_resize, step + 1)

                    animate_resize()

    def get_current_month_name(self):
        months_in_russian = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        current_month = datetime.datetime.now().month
        return months_in_russian[current_month - 1]

    def init_login_frame(self):
        frame = tk.Frame(self.root)
        self.frames["login_frame"] = frame
        frame.configure(bg="#000000")
        frame.option_add("*Font", "Helvetica 14")
        frame.option_add("*Button.relief", "flat")
        frame.option_add("*Button.highlightThickness", 0)
        frame.option_add("*Button.background", "#FFFFFF")
        frame.option_add("*Button.foreground", "#000000")
        frame.option_add("*Button.activeBackground", "#555555")
        frame.option_add("*Label.background", "#000000")
        frame.option_add("*Label.foreground", "#FFFFFF")
        frame.option_add("*Entry.background", "#333333")
        frame.option_add("*Entry.foreground", "#FFFFFF")
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
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                        for ele in range(0, 8*6, 8)][::-1])
        hostname = socket.gethostname()
        print(f"MAC: {mac}, Hostname: {hostname}")
        if hashlib.sha256(mac.encode()).hexdigest() in Model.allowed_macs and hostname in Model.allowed_hosts:
            password = self.password_var.get()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if hashed_password == Model.hashed_password:
                self.show_frame("employee_frame")
            else:
                self.wrongAttempts += 1
                if self.wrongAttempts >= 3:
                    messagebox.showerror(
                        "Ошибка", "Слишком много неправильных попыток. Приложение будет закрыто.")
                    self.root.quit()
                    self.root.destroy()
                    sys.exit(0)
                else:
                    messagebox.showerror(
                        "Ошибка", "Неверный логин или пароль. Попробуйте еще раз.")
        else: 
            print("Unauthorized access attempt detected.")
        


    def init_employee_frame(self):
        frame = tk.Frame(self.root, bg="#000000")
        self.frames["employee_frame"] = frame
        frame.configure(bg="#000000")
        self.root.configure(bg="#000000")
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
        dropdown_width = 18
        for i in range(3):
            employee_var = tk.StringVar(frame)
            employee_var.set("Выберете работника")
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
            self.workplace_var.set("Июнь")
            workplace_menu = tk.OptionMenu(
                frame, self.workplace_var, "Июнь", "Пик", "Лондон Молл", "Коменда")
            workplace_menu.configure(width=dropdown_width)
            workplace_menu.grid(row=5, column=1, pady=10)

        tk.Button(frame, text="Далее", command=self.preview_employees, bg="white", fg="black").grid(
            row=6, column=1, pady=10)

    def preview_employees(self):
        """
        Opens a preview window displaying the selected employees and their details.
        This method collects information about up to three employees from the UI, 
        filters out entries with placeholder values, and displays a formatted preview 
        in a new Toplevel window. The preview includes employee name, type, and shift, 
        as well as the selected workplace. The user can confirm or reject the selection 
        using provided buttons.
        UI Elements Created:
            - Toplevel window with a formatted text widget showing employee details.
            - Two buttons: "Согласен" (Agree) and "Не согласен" (Disagree), 
              which trigger the agreeToDisagree method with appropriate arguments.
        Filtering:
            - Employees with names "Пропуск" or "Выберете работника" are excluded from the preview.
        Side Effects:
            - Opens a new window for preview.
            - Calls agreeToDisagree based on user interaction.
        """
        
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

        col_widths = [max(len(str(employee[i])) for employee in employee_preview if isinstance(
            employee, list)) + 2 for i in range(3)]
        col_widths.append(20)

        text_widget.insert(
            "end", f"{'Имя':<{col_widths[0]}}{'Тип':<{col_widths[1]}}{'Смена':<{col_widths[2]}}\n")
        text_widget.insert("end", "-" * sum(col_widths) + "\n")

        for employee in employee_preview:
            if isinstance(employee, list):
                text_widget.insert(
                    "end", f"{employee[0]:<{col_widths[0]}}{employee[1]:<{col_widths[1]}}{employee[2]:<{col_widths[2]}}\n"
                )
            else:
                text_widget.insert(
                    "end", f"\n{employee.center(sum(col_widths))}\n")

        text_widget.config(state="disabled")
        button_frame = tk.Frame(preview_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Согласен", command=lambda: self.agreeToDisagree(
            True, preview_window=preview_window, next_frame="payment_frame", key="emp"), bg="white", fg="black").pack(side="left", padx=10)
        tk.Button(button_frame, text="Не согласен", command=lambda: self.agreeToDisagree(
            False, preview_window=preview_window, act_frame="employee_frame", key="emp"), bg="white", fg="black").pack(side="right", padx=10)

    def get_employee_request(self):
        """
        Collects employee selection data from the UI, processes it, and updates related attributes and frames.
        This method performs the following steps:
        1. Gathers employee information from UI variables and widgets for three employees.
        2. Appends the selected workplace to the employee request list.
        3. Filters out entries where the employee selection is "Пропуск" or "Выберете работника".
        4. Updates the UI to show the payment frame.
        5. Sets the address and employee request attributes.
        6. Updates the employee list in the updater and triggers an update.
        Side Effects:
            - Prints the raw employee request list.
            - Changes the current frame to "payment_frame".
            - Updates `self.address`, `self.employee_request`, and `self.updater.employee_list`.
            - Calls `self.updater._update_emp()` to refresh employee data.
        """

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
        selected = [
            var.get() for var in self.employee_vars
            if var.get() != "Выберете работника" and var.get() != "Пропуск"
        ]
        for i, (var, menu_widget) in enumerate(zip(self.employee_vars, self.employee_menus)):
            menu = menu_widget["menu"]
            menu.delete(0, "end")
            for emp in self.employees:
                if emp not in selected or emp == var.get():
                    menu.add_command(
                        label=emp,
                        command=lambda value=emp, v=var: v.set(value)
                    )
            if var.get() not in [emp for emp in self.employees if emp not in selected or emp == var.get()]:
                var.set("Выберете работника")

    def init_payment_frame(self):
        """
        Initializes and configures the payment frame UI for the application.

        This method sets up all widgets and layout for the payment process, including:
        - Dropdowns for payment type, product type, and product selection.
        - Dynamic visibility of widgets based on selected product type (e.g., people count, use of certificate/abonement).
        - Date and time selection widgets with options to set to current date/time.
        - Payment method selection, including support for split payments and dynamic entry fields.
        - Calculation and validation of payment amounts, with error and status feedback.
        - Navigation buttons for proceeding to summary, returning to employee frame, and closing the shift.
        - Percentage entry for partial/pre-payment types.
        - All widgets are arranged using a grid layout and are dynamically shown/hidden based on user interaction.

        Traces and event handlers are set up to update the UI in response to user input.
        """

        self.root.bind("<Configure>", self.enforce_frame_size)
        dropdown_width = 18
        frame = tk.Frame(self.root, bg="black")
        self.frames["payment_frame"] = frame
        for i in range(10):
            frame.grid_rowconfigure(i, minsize=50)
        for j in range(10):
            frame.grid_columnconfigure(j, minsize=100)

        tk.Label(frame, text="Выберите тип оплаты", anchor="w").grid(
            row=2, column=0, pady=10, sticky="w")

        tk.Label(frame, text="Выберите товар", anchor="w").grid(
            row=1, column=0, pady=10, sticky="w")

        self.payment_type_var = tk.StringVar(frame)
        self.payment_type_var.set("Полная оплата")
        payment_type_menu = tk.OptionMenu(
            frame, self.payment_type_var, "Доплата", "Предоплата", "Полная оплата")
        payment_type_menu.configure(width=dropdown_width)
        payment_type_menu.grid(row=2, column=1, pady=10)

        tk.Label(frame, text="Выберите Тип товара", anchor="w").grid(
            row=0, column=0, pady=10, sticky="w")
        self.product_type_var = tk.StringVar(frame)
        self.product_type_var.set("Тип товара")
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
            """
            Updates the visibility of the people count label and entry widgets based on the selected product type.
            If the selected product type is "Время" (Time) or "Одиночная игра" (Single Game), the people count label and entry are shown.
            Otherwise, they are hidden.
            Args:
                *args: Variable length argument list, typically used for Tkinter trace callbacks.
            """

            def fade_in(widget):
                widget.grid()
            def fade_out(widget):
                widget.grid_forget()
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
            """
            Updates the visibility and label of the 'useABOcERT' widget based on the selected product type.

            If the selected product type is either "Абонемент" or "Сертификат", the widget is displayed with a label
            prompting the user to use the selected product type. Otherwise, the widget is hidden.

            Args:
                *args: Variable length argument list, typically used for Tkinter trace callbacks.
            """
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

        self.year_var = tk.StringVar(frame)
        self.year_var.set(str(self.today_date.year))
        year_options = [str(year)
                        for year in range(self.today_date.year, 2027)]
        year_menu = tk.OptionMenu(frame, self.year_var, *year_options)
        year_menu.configure(width=dropdown_width)
        year_menu.grid(row=4, column=3, pady=10)

        self.month_var = tk.StringVar(frame)
        month_options = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        self.month_var.set(month_options[self.today_date.month - 1])
        self.time_var = tk.StringVar(frame)
        self.time_var.set("10:00")

        tk.Label(frame, text="Введите время (чч:мм)").grid(
            row=3, column=4, pady=10)

        self.time_entry = tk.Entry(frame, textvariable=self.time_var)
        self.time_entry.grid(row=4, column=4, pady=10, padx=10)

        tk.Button(frame, text="Сегодня", command=self.set_today_date, bg="white", fg="black").grid(
            row=4, column=5, pady=10)

        tk.Button(frame, text="Сейчас", command=self.set_current_time, bg="white", fg="black").grid(
            row=3, column=5, pady=10)

        month_menu = tk.OptionMenu(frame, self.month_var, *month_options)
        month_menu.configure(width=dropdown_width)
        month_menu.grid(row=5, column=3, pady=10)

        self.day_var = tk.StringVar(frame)
        self.day_var.set(str(self.today_date.day))
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

        self.payment_methods = ["Наличные по кассе", "Карта", "QR/СБП", "Н/П"]
        self.payment_entries = []
        self.payment_dropdown_var = tk.StringVar(frame)
        self.payment_dropdown_var.set(self.payment_methods[0])
        payment_dropdown = tk.OptionMenu(
            frame, self.payment_dropdown_var, *self.payment_methods)
        payment_dropdown.configure(width=dropdown_width)
        payment_dropdown.grid(row=6, column=1, pady=5)

        def update_payment_method_visibility(*args):
            """
            Updates the visibility and layout of payment method input fields based on the state of the split payment option.
            If the split payment option is enabled (`self.split_payment_var.get()` is True), dynamically creates and displays
            entry fields for each payment method in `self.payment_methods`, allowing the user to input amounts for each method.
            Hides the single payment method dropdown.
            If the split payment option is disabled, removes the dynamically created payment method entry fields and restores
            the single payment method dropdown for user selection.
            Args:
                *args: Variable length argument list, typically used for Tkinter variable trace callbacks.
            """

            if self.split_payment_var.get():
                for i, method in enumerate(self.payment_methods):
                    tk.Label(frame, text=f"{method}:", anchor="w").grid(
                        row=6 + i, column=0, pady=5, sticky="w")
                    payment_var = tk.StringVar(frame)
                    tk.Entry(frame, textvariable=payment_var).grid(
                        row=6 + i, column=1, pady=5)
                    self.payment_entries.append(payment_var)
                payment_dropdown.grid_forget()
            else:
                for widget in frame.grid_slaves():
                    if int(widget.grid_info()["row"]) >= 6 and (widget.grid_info()["column"] == 1 or widget.grid_info()["column"] == 0) and not isinstance(widget, tk.Button):
                        widget.grid_forget()
                self.payment_entries.clear()
                payment_dropdown.grid(row=6, column=1, pady=5)
                self.payment_dropdown_var.set(self.payment_methods[0])

        self.split_payment_var.trace_add(
            "write", update_payment_method_visibility)

        tk.Button(frame, text="Закрытие смены", command=self.open_CSF, bg="white", fg="black").grid(
            row=11, column=4, pady=10)
        self.percentage_label = tk.Label(frame, text="Проценты")
        self.percentage_entry_var = tk.StringVar(frame)
        self.percentage_entry = tk.Entry(
            frame, textvariable=self.percentage_entry_var)

        def calculate_remaining_balance():
            """
            Calculates the remaining balance based on user-entered payment amounts and updates the UI accordingly.
            This function:
            - Sums all valid integer values entered in the payment entry fields.
            - Calculates the remaining balance by subtracting the total entered amount from the actual payment amount.
            - Updates the UI to reflect the payment status:
                - Highlights entry fields in red and displays an error if the entered sum exceeds the required amount.
                - Shows the remaining balance in red if the payment is incomplete.
                - Resets entry field colors and displays a success message if the payment is exact.
                - Warns the user if no valid data is entered.
            - Handles invalid input by displaying an error message.
            Exceptions:
                ValueError: If any entry contains invalid data that cannot be converted to an integer.
            """

            try:
                total_entered = sum(
                    int(entry.get()) for entry in self.payment_entries if entry.get().isdigit()
                )
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
            """
            Updates the visibility of the percentage label and entry widgets based on the selected payment type.
            If the payment type is either "Доплата" (additional payment) or "Предоплата" (prepayment), 
            the percentage label and entry widgets are displayed in the UI grid. Otherwise, they are hidden.
            Args:
                *args: Variable length argument list to support callback usage (e.g., with Tkinter variable tracing).
            """

            if self.payment_type_var.get() in ["Доплата", "Предоплата"]:
                self.percentage_label.grid(row=2, column=2, pady=10)
                self.percentage_entry.grid(row=2, column=3, pady=10)
            else:
                self.percentage_label.grid_forget()
                self.percentage_entry.grid_forget()

        self.payment_type_var.trace_add("write", update_percentage_visibility)

        def update_date_visibility(*args):
            """
            Updates the visibility and placement of date and time selection widgets based on the selected product type.
            If the selected product type is "Сертификат" or "Абонемент", all date and time widgets are hidden and their values are reset.
            Otherwise, the date and time widgets (year, month, day menus, time entry, and related labels/buttons) are displayed in their respective grid positions.
            Args:
                *args: Variable length argument list, used to support callback signatures (e.g., for Tkinter variable tracing).
            Side Effects:
                Modifies the visibility and values of various Tkinter widgets related to date and time selection within the UI frame.
            """

            if self.product_type_var.get() in ["Сертификат", "Абонемент"]:
                year_menu.grid_forget()
                month_menu.grid_forget()
                day_menu.grid_forget()
                self.time_entry.grid_forget()
                self.time_var.set("")
                self.date_var.set("")
                self.time_var.set("10:00")
                for widget in frame.grid_slaves():
                    if widget.cget("text") in ["Выберите дату", "Введите время (чч:мм)", "Сегодня", "Сейчас"]:
                        widget.grid_forget()
                self.date_var.set("")
            else:
                self.time_entry.grid(row=4, column=4, pady=10, padx=10)
                tk.Label(frame, text="Выберите дату", anchor="w").grid(
                    row=3, column=3, pady=10, sticky="w")
                tk.Label(frame, text="Введите время (чч:мм)").grid(
                    row=3, column=4, pady=10)
                year_menu.grid(row=4, column=3, pady=10)
                month_menu.grid(row=5, column=3, pady=10)
                day_menu.grid(row=6, column=3, pady=10)
                tk.Button(frame, text="Сегодня", command=self.set_today_date,  bg="white", fg="black").grid(
                    row=4, column=5, pady=10)
                tk.Button(frame, text="Сейчас", command=self.set_current_time,  bg="white", fg="black").grid(
                    row=3, column=5, pady=10)

        self.product_type_var.trace_add("write", update_date_visibility)

    def set_today_date(self):
        self.year_var.set(str(self.today_date.year))
        self.month_var.set(str(self.get_current_month_name()))
        self.day_var.set(str(self.today_date.day))

    def set_current_time(self):
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

        self.requests_tree = tk.ttk.Treeview(frame, columns=(
            "Тип товара, Товар", "Время чека", "Количество человек", "Карта",
            "QR/СБП", "Наличные по кассе", "НП", "Игра AW",
            "Дата игры", "Время"
        ), show="headings", height=15)

        for col in self.requests_tree["columns"]:
            self.requests_tree.heading(col, text=col)
            self.requests_tree.column(col, width=120, anchor="center")

        self.requests_tree.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10)

        self.update_requests_tree()

        tk.Button(frame, text="Закрыть смену", command=self.close_shift, bg="white", fg="black").grid(
            row=2, column=0, pady=10)
        tk.Button(frame, text="Назад", command=lambda: self.show_frame("summary_frame"), bg="white", fg="black").grid(
            row=2, column=1, pady=10)

    def update_requests_tree(self):
        """
        Updates the requests_tree widget with the latest request data.
        This method clears all existing entries from the requests_tree widget and repopulates it
        with the current data from self.updater.all_requests. If there are no requests available,
        it inserts a placeholder row indicating that there is no data.
        The method expects self.updater.all_requests to be a pandas DataFrame with the following columns:
            - "Тип товара"
            - "Товар"
            - "Время чека"
            - "Количество человек"
            - "Карта"
            - "QR/СБП"
            - "Наличные по кассе"
            - "НП"
            - "Игра AW"
            - "Дата игры"
            - "Время"
        If the DataFrame is empty, a row with "Нет данных" is inserted for each column.
        """

        for item in self.requests_tree.get_children():
            self.requests_tree.delete(item)

        if not self.updater.all_requests.empty:
            for _, request in self.updater.all_requests.iterrows():
                self.requests_tree.insert("", "end", values=(
                    str(request["Тип товара"]+" " +
                        request["Товар"]), request["Время чека"],
                    request["Количество человек"], request["Карта"], request["QR/СБП"],
                    request["Наличные по кассе"], request["НП"], request["Игра AW"],
                    request["Дата игры"], request["Время"]
                ))
        else:
            self.requests_tree.insert("", "end", values=(
                "Нет данных",) * len(self.requests_tree["columns"]))

    def open_CSF(self):
        self.update_requests_tree()
        self.show_frame("closeShift_frame")

    def close_shift(self):
        if tk.messagebox.askyesno("Подтверждение", "Вы уверены, что хотите закрыть смену?"):
            tk.messagebox.showinfo("Закрытие смены", "Смена успешно закрыта!")
            self.on_close()

    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.grid_forget()
        frame = self.frames[frame_name]
        frame.grid(row=0, column=0, padx=10, pady=10)
        frame.update_idletasks()

    def update_dropdown(self, *args):
        """
        Updates the options in the product dropdown menu based on the selected product type.
        The method checks the current value of `self.product_type_var` and sets the dropdown options accordingly:
            - "Тариф": Sets options to ["STD", "HARD", "VIP"].
            - "Время": Sets options to time intervals from 30 to 300 minutes in 30-minute steps.
            - "Одиночная игра": Sets options to time intervals from 15 to 315 minutes in 15-minute steps.
            - "Сертификат": Sets options to certificate values in rubles.
            - "Абонемент": Sets options to subscription prices in rubles.
        After updating the dropdown menu, the first option is selected by default.
        Args:
            *args: Additional arguments (not used, but allows compatibility with variable argument callbacks).
        """

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
        """
        Displays a preview window summarizing the current data.
        This method creates a new top-level window containing a read-only text widget
        that displays key-value pairs from `self.data_summary`. It also provides two buttons:
        "Согласен" (Agree) and "Не согласен" (Disagree), which call `self.agreeToDisagree`
        with the user's choice and close the preview window. The preview window is intended
        to allow the user to review and confirm the data before proceeding to the next step
        (e.g., the payment frame).
        """

        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("Предварительный просмотр")
        self.preview_window.geometry("600x500")

        text_widget = tk.Text(self.preview_window, wrap="word",
                              font=("Helvetica", 12))
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        for key, value in self.data_summary.items():
            text_widget.insert("end", f"{key}: {value}\n")

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
        Handles the user's agreement or disagreement with a request and updates the UI accordingly.
        If the user agrees (`isAgreed` is True), performs an action based on the `key` parameter:
            - If `key` is "sell", sends a sell request using `self.updater.catch_req_sell`.
            - If `key` is "emp", processes an employee request using `self.get_employee_request`.
        In both cases, displays a confirmation message, switches to the `next_frame`, and closes the `preview_window`.
        If the user disagrees (`isAgreed` is False), displays a message prompting for clarification,
        switches to the `act_frame`, and closes the `preview_window`.
        Args:
            isAgreed (bool): Indicates whether the user agreed to the request.
            preview_window (tk.Toplevel): The preview window to be destroyed after the action.
            act_frame (str, optional): The frame to show if the user disagrees. Defaults to "payment_frame".
            next_frame (str, optional): The frame to show if the user agrees. Defaults to "summary_frame".
            key (str, optional): Determines the action to perform if agreed ("sell" or "emp"). Defaults to "sell".
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
        """
        Collects and summarizes form data from various UI elements into a dictionary (`self.data_summary`).

        The method gathers values such as product type, product, payment details, number of people, date, time, percentages, comments, and payment breakdowns (including split payments) from the UI variables. It also applies specific business logic for calculating the number of people and payment allocations based on the selected options.

        After assembling the data, it calls `self.show_preview()` to display a preview of the collected information.

        Fields in `self.data_summary` include:
            - "Тип товара": Selected product type.
            - "Товар": Selected product.
            - "Стоимость": Actual payment amount.
            - "Способ оплаты": Payment method or "Раздельная" if split payment is enabled.
            - "Тип оплаты": Type of payment.
            - "Количество человек": Number of people, calculated based on product type and product.
            - "Дата": Selected date.
            - "Время": Selected time.
            - "Проценты": Percentage for partial/prepayment, or "100" otherwise.
            - "Время чека": Check time.
            - "Комментарий": User comment.
            - "НП", "Наличные по кассе", "Карта", "QR/СБП": Payment breakdowns by method.
            - "Игра AW": Calculated value based on payment type, product type, and percentage.

        Returns:
            None
        """

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
        """
        Navigates to the previous frame in the application's frame order.
        This method determines the currently visible frame, finds its position in the
        frame order, and if it is not the first frame, switches the view to the previous frame.
        """

        current_frame = None
        for frame_name, frame in self.frames.items():
            if frame.winfo_ismapped():
                current_frame = frame_name
                break

        if current_frame:
            current_index = self.frame_order.index(current_frame)
            if current_index > 0:
                previous_frame = self.frame_order[current_index - 1]
                self.show_frame(previous_frame)

    def openUI(self, root):
        root.mainloop()
