import os
import sys
import tkinter as tk

import gspread
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from OptimizedWindows import OptimizedWindows
from ui import UIManager

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    uim = None

    # Get the absolute path using resource_path function
    json_path = resource_path("key.json")

    SERVICE_ACCOUNT_FILE = json_path


    SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_FILE, SCOPES)

    client = gspread.authorize(credentials)

    service = build('sheets', 'v4', credentials=credentials)
    sheetWAGES = client.open("! Таблица расчета зарплаты").worksheet("WGSlist")

    def get_non_empty_cells(sheet, cell_range):
        cell_values = sheet.range(cell_range)
        non_empty_cells = [cell.value for cell in cell_values if cell.value]
        return non_empty_cells

    non_empty_cells = get_non_empty_cells(sheetWAGES, 'C97:C119')

    rootadd = tk.Tk()
    rootadd.resizable(False,False)
    rootadd.geometry(f"{400}x{400}")
    employee_label = tk.Label(rootadd, text="Выберете сотрудника и арену")
    employee_label.grid(row=1, column=0, padx=10, pady=5)
    additional_variable = tk.StringVar(rootadd)
    additional_options = non_empty_cells
    employee_dropdown = tk.OptionMenu(rootadd, additional_variable, *additional_options)
    employee_dropdown.grid(row=1, column=1, padx=10, pady=5)

    additional_optionsplace = ["Июнь","ПИК","Лондон Молл"]
    additional_variableplace = tk.StringVar(rootadd)
    additional_variableplace.set(additional_optionsplace[0])  # default value

    additional_label = tk.Label(rootadd, text="Арена")
    additional_label.grid(row=0, column=0, padx=10, pady=5)
    additional_dropdown = tk.OptionMenu(rootadd, additional_variableplace, *additional_optionsplace)
    additional_dropdown.grid(row=0, column=1, padx=10, pady=5)
    rootadd.mainloop()
    

    root = tk.Tk()
    root.resizable(False,False)

    scaling_factor, screen_height, screen_width = OptimizedWindows.checkWindowDPI()

    window_width, window_height, position_x, position_y, scale_factor = OptimizedWindows.adjust_window_size(
    screen_width, screen_height, 440, 460)
    root.geometry(f"{440}x{460}+{position_x}+{position_y}")
    root.attributes('-topmost', 1)
    root.after(5000, lambda: root.attributes('-topmost', 0))
    uim = UIManager(root,sheetWAGES,non_empty_cells)
    uim.getCellAddrToday(sheetWAGES)
    uim.openUI(root)