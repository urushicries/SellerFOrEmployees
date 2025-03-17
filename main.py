from ui import UIManager
import tkinter as tk
import gspread
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import os
import sys
from OptimizedWindows import OptimizedWindows
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

    root = tk.Tk()
    root.resizable(False,False)

    scaling_factor, screen_height, screen_width = OptimizedWindows.checkWindowDPI()

    window_width, window_height, position_x, position_y, scale_factor = OptimizedWindows.adjust_window_size(
    screen_width, screen_height, 440, 430)
    root.geometry(f"{440}x{430}+{position_x}+{position_y}")

    root.geometry()
    uim = UIManager(root,sheetWAGES)
    uim.getCellAddrToday(sheetWAGES)
    uim.openUI(root)