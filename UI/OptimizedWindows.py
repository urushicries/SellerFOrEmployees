import ctypes
import sys
import os
import tkinter as tk


class OptimizedWindows:
    """Класс, содержащий утилитарные методы для настройки DPI, определения пути исполняемого файла
    и проверки масштабирования окна.

    Методы:
        optForWindowSize() -> None:
            Устанавливает DPI-осведомленность процесса для предотвращения размытия интерфейса.

        optIfAppIsCompiled() -> str:
            Определяет путь к исполняемому файлу, учитывая запуск из скомпилированного пакета (PyInstaller).

        checkWindowDPI() -> float:
            Проверяет масштабирование окна, возвращая коэффициент DPI.
    """

    @staticmethod
    def optForWindowSize() -> None:
        """Устанавливает DPI-осведомленность процесса для предотвращения размытия интерфейса."""
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(
                2)  # Per-monitor DPI awareness
        except AttributeError:
            pass

    @staticmethod
    def optIfAppIsCompiled() -> str:
        """Определяет путь к исполняемому файлу, учитывая запуск из скомпилированного пакета (PyInstaller)."""
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return os.path.abspath(os.path.dirname(__file__))

    @staticmethod
    def checkWindowDPI():
        """Проверяет масштабирование окна, возвращая коэффициент DPI."""
        root = tk.Tk()
        scaling_factor = root.winfo_fpixels('1i') / 96  # Базовый DPI — 96
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        return scaling_factor, screen_height, screen_width

    @staticmethod
    def adjust_window_size(screen_width, screen_height, width, height):
        """
        Этот метод настраивает размер и позицию окна в зависимости от разрешения экрана и желаемых размеров.

        Аргументы:
            screen_width (int): Ширина экрана.
            screen_height (int): Высота экрана.
            width (int): Желаемая ширина окна.
            height (int): Желаемая высота окна.

        Возвращает:
            tuple: Новый размер окна (ширина, высота) и его позиция (x, y).
        """
        # Базовое разрешение, относительно которого настраиваем масштаб
        base_width, base_height = screen_width, screen_height

        # Вычисляем коэффициент масштабирования
        scaling_factor = min(width / base_width, height / base_height)

        # Подгоняем итоговый коэффициент
        scale_factor = 1 / scaling_factor if scaling_factor > 1 else scaling_factor

        # Вычисляем итоговый размер окна с учетом масштабирования
        window_width = int(width * scale_factor)
        window_height = int(height * scale_factor)

        # Рассчитываем позицию окна для центрирования
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2

        return window_width, window_height, position_x, position_y, scale_factor
