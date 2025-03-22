import os
import sys
import tkinter as tk

import gspread
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from OptimizedWindows import OptimizedWindows
from ui import UIManager
from updater import Updater


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
    json_path = resource_path("komot-aw.json")

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

    root = tk.Tk()
    root.resizable(False, False)

    sheetKOM = None
    shtKOM_id = "1vAVIeR4UWVAx7KwAR6x23yT_Ha1KTuc8VjcTVjnTM_8"
    client = client
    sheetPIK = None
    shtPIK_id = "1DlRu9fzlzJj4Uor4FvXp9IEwi4FJfKq4bD7cN9GbtW0"
    sheetJUNE = None
    shtJUN_id = "17tnMhq5fp9IEatRqLnlyeemhbNP4aGOblGWpJ4_ABYs"
    sheetLM = None
    shtLM_id = "1PIICQiP3Tr1gmw4CsQ1bxVbkaU4mOPm_6409W-b7K3E"

    config = {
        'root': root,
        'client': client,
        'Updater': None,  # Placeholder for Updater instance
        'service': service,
        'sheetWAGES': sheetWAGES,
        'shtKOM_id': shtKOM_id,
        'shtPIK_id': shtPIK_id,
        'shtJUN_id': shtJUN_id,
        'shtLM_id': shtLM_id,
        'ui': None,  # Placeholder for UIManager instance
        'list_employee': non_empty_cells
    }

    updmanager = Updater(config)
    uim = UIManager(config)

    # Update config with actual instances
    config['Updater'] = updmanager
    config['ui'] = uim

    scaling_factor, screen_height, screen_width = OptimizedWindows.checkWindowDPI()

    # Calculate position to center the window on the screen
    position_x = (screen_width - 300) // 2
    position_y = (screen_height - 300) // 2

    window_width, window_height = 300, 300
    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    root.attributes('-topmost', 1)
    root.after(5000, lambda: root.attributes('-topmost', 0))

    uim.getCellAddrToday(sheetWAGES)

    uim.openUI(root)
