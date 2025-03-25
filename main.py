import os
import sys
import tkinter as tk

import gspread
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from OptimizedWindows import OptimizedWindows
from ui import UIManager
from updater import Updater
from datetime import datetime


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
    json_path = resource_path("emp.json")

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
    non_empty_cells.append("Пропуск")
    root = tk.Tk()
    root.resizable(False, False)

    def get_current_month_name():
        """Returns the Russian name of the current month."""
        months_in_russian = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        current_month = datetime.now().month
        return months_in_russian[current_month - 1]

    sheetPIK = client.open("Пик отчет").worksheet(
        f"{get_current_month_name()}25")
    sheetJUN = client.open("Июнь отчет").worksheet(
        f"{get_current_month_name()}25")
    sheetLM = client.open("Лондон отчет").worksheet(
        f"{get_current_month_name()}25")
    sheetKOM = client.open("Коменда отчет").worksheet(
        f"{get_current_month_name()}25")

    config = {
        'root': root,
        'client': client,
        'Updater': None,  # Placeholder for Updater instance
        'service': service,
        'sheetWAGES': sheetWAGES,
        'sheetPIK': sheetPIK,
        'sheetJUN': sheetJUN,
        'sheetLM': sheetLM,
        'sheetKOM': sheetKOM,
        'ui': None,  # Placeholder for UIManager instance
        'list_employee': non_empty_cells
    }

    # Create the UIManager instance first
    uim = UIManager(config)
    config['ui'] = uim  # Assign the UIManager instance to the config

    # Now create the Updater instance
    updmanager = Updater(config)
    config['Updater'] = updmanager  # Assign the Updater instance to the config
    uim.updater = updmanager
    scaling_factor, screen_height, screen_width = OptimizedWindows.checkWindowDPI()

    # Calculate position to center the window on the screen
    position_x = (screen_width - 300) // 2
    position_y = (screen_height - 300) // 2

    window_width, window_height = 300, 300
    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    root.attributes('-topmost', 1)
    root.after(5000, lambda: root.attributes('-topmost', 0))

    uim.openUI(root)
