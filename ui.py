import tkinter as tk
import datetime
from FFCWP import ffcwp


class UIManager:
    def __init__(self, root, sheetwages,employees):
        self.additional_options = employees
        self.additional_variable = tk.StringVar(root)
        self.additional_variable.set(self.additional_options[0])  # default value


        self.today_date = str(datetime.date.today())
        self.root = root
        self.root.title("Добавление продажи в отчет")
        label1 = tk.Label(root, text="Тариф/Время")
        label1.grid(row=2, column=0, padx=10, pady=5)
        labeltovar = tk.Label(root, text="Выберете товар")
        labeltovar.grid(row=3, column=0, padx=10, pady=5)
        options = ["Тариф", "Время","Одиночная игра","Абонемент","Сертификат"]
        self.variable = tk.StringVar(root)
        self.variable.set(options[0])  # default value
        dropdown = tk.OptionMenu(root, self.variable, *options)
        dropdown.grid(row=2, column=1, padx=10, pady=5)

        self.second_variable = tk.StringVar(root)
        self.second_dropdown = tk.OptionMenu(root, self.second_variable, "")
        self.second_dropdown.grid(row=3, column=1, padx=10, pady=5)

        self.variable.trace_add("write", self.update_dropdown)
        self.update_dropdown()

        label2 = tk.Label(root, text="Время начала сессии")
        label2.grid(row=4, column=0, padx=10, pady=5)
        entry2 = tk.Entry(root)
        entry2.grid(row=4, column=1, padx=10, pady=5)

        label3 = tk.Label(root, text="Количество человек")
        label3.grid(row=5, column=0, padx=10, pady=5)
        entry3 = tk.Entry(root)
        entry3.grid(row=5, column=1, padx=10, pady=5)

        label4 = tk.Label(root, text="Карта")
        label4.grid(row=6, column=0, padx=10, pady=5)
        entry4 = tk.Entry(root)
        entry4.grid(row=6, column=1, padx=10, pady=5)

        label5 = tk.Label(root, text="QR/СБП")
        label5.grid(row=7, column=0, padx=10, pady=5)
        entry5 = tk.Entry(root)
        entry5.grid(row=7, column=1, padx=10, pady=5)

        label6 = tk.Label(root, text="Наличные по кассе")
        label6.grid(row=8, column=0, padx=10, pady=5)
        entry6 = tk.Entry(root)
        entry6.grid(row=8, column=1, padx=10, pady=5)

        label7 = tk.Label(root, text="Наличные не пробитые по кассе")
        label7.grid(row=9, column=0, padx=10, pady=5)
        entry7 = tk.Entry(root)
        entry7.grid(row=9, column=1, padx=10, pady=5)

        label8 = tk.Label(root, text="Игра AW")
        label8.grid(row=10, column=0, padx=10, pady=5)
        entry8 = tk.Entry(root)
        entry8.grid(row=10, column=1, padx=10, pady=5)

        label9 = tk.Label(root, text="Комментарий")
        label9.grid(row=11, column=0, padx=10, pady=5)
        entry9 = tk.Entry(root)
        entry9.grid(row=11, column=1, padx=10, pady=5)

        add_button = tk.Button(root, text="Добавить в отчет")
        add_button.grid(row=12, column=0, columnspan=2, pady=10)


    def update_dropdown(self, *args):
        if self.variable.get() == "Тариф":
            new_options = ["STD", "HARD", "VIP"]
        elif self.variable.get() == "Время":
            new_options = [f"{i} мин" for i in range(30, 330, 30)]
        elif self.variable.get() == "Одиночная игра": 
            new_options = [f"{i} мин" for i in range(15, 325, 15)]
        elif self.variable.get() == "Сертификат":
            new_options = [f"На {i} рублей" for i in [1000, 3000, 5000, 10000]]
        elif self.variable.get() == "Абонемент":
            new_options = [f"За {i} рублей" for i in [2500,4500,6500]]
        menu = self.second_dropdown["menu"]
        menu.delete(0, "end")
        for option in new_options:
            menu.add_command(label=option, command=lambda value=option: self.second_variable.set(value))
        self.second_variable.set(new_options[0])

    def openUI(self, root):
        root.mainloop()

    def getCellAddrToday(self, sheetwages):
        addr = ffcwp.find_first_matching_cell(sheetwages, [self.today_date])
        return addr
