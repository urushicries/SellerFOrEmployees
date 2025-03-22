import re


class ffcwp:
    """ 
    The `ffcwp` class provides static methods to find specific patterns in the first column of a sheet and process data from multiple sheets based on a given pattern.

        Methods:
            find_first_matching_cell(sheet, patterns):

            ffcwp15(sheet):

            ffcwpend(sheet):

            makeDataFromSheets(pattern: int, *sheets) -> tuple | None:
                Processes data from sheets by some pattern.
                    pattern (int): Key for calculation either until the end of the month or until the middle.
                    sheets (tuple): Report tables.
                    tuple | None: A tuple containing data from the sheets based on the pattern, or None if the pattern is not recognized.
        """
    @staticmethod
    def find_first_matching_cell(sheet, patterns):
        """
        Finds the first cell in the first column that matches any of the given patterns.
        Args:
            sheet (object): The sheet object to search.
            patterns (list): List of compiled regex patterns to match.
        Returns:
            int | None: The row number of the first matching cell, or None if no match is found.
        """
        column_data = sheet.col_values(1)  # Get all values in the first column

        for row_num, value in enumerate(column_data, start=1):
            for pattern in patterns:
                if pattern.match(value):
                    return row_num
        return None

    @staticmethod
    def ffcwp15(sheet):
        """
        Finds the first cell in the first column with the format '15.xx.xxxx'.
        Args:
            sheet (object): The sheet object to search.
        Returns:
            int | None: The row number of the first matching cell, or None if no match is found.
        """
        pattern = re.compile(r"^15\.\d{2}\.\d{4}$")
        return ffcwp.find_first_matching_cell(sheet, [pattern])

    @staticmethod
    def ffcwpend(sheet):
        """
        Finds the first cell in the first column with one of the following formats:
        '31.xx.xxxx', '30.xx.xxxx', '29.xx.xxxx', or '28.xx.xxxx'.
        Priority: '31.xx.xxxx' first, then the others in order.
        Args:
            sheet (object): The sheet object to search.
        Returns:
            int | None: The row number of the first matching cell, or None if no match is found.
        """
        patterns = [
            re.compile(r"^31\.\d{2}\.\d{4}$"),
            re.compile(r"^30\.\d{2}\.\d{4}$"),
            re.compile(r"^29\.\d{2}\.\d{4}$"),
            re.compile(r"^28\.\d{2}\.\d{4}$")
        ]
        return ffcwp.find_first_matching_cell(sheet, patterns)

    @staticmethod
    def makeDataFromSheets(pattern: int, *sheets) -> tuple | None:
        """
        Procesess data from  sheets by some pattern.
        Args:
            sheets(tuple): таблицы отчетов
            pattern(int):ключ для расчет либо до  конца месяца либо до середины
        Returns:
            nothing
        """
        sheetKOM, sheetPIK, sheetJUNE, sheetLM = sheets
        if pattern == 15:
            # 1-15 числа
            data15KOMENDA = sheetKOM.get(
                f'A1:M{ffcwp.ffcwp.ffcwp15(sheetKOM)}')
            data15PIK = sheetPIK.get(f'A1:M{ffcwp.ffcwp.ffcwp15(sheetPIK)}')
            data15JUNE = sheetJUNE.get(f'A1:M{ffcwp.ffcwp15(sheetJUNE)}')
            data15LM = sheetLM.get(f'A1:M{ffcwp.ffcwp15(sheetLM)}')
            return data15KOMENDA, data15PIK, data15LM, data15JUNE

        if pattern == 31:
            # 15-31 числа
            data31KOMENDA = sheetKOM.get(
                f'A{ffcwp.ffcwp15(sheetKOM)}:M{ffcwp.ffcwpend(sheetKOM)+20}')
            data31PIK = sheetPIK.get(
                f'A{ffcwp.ffcwp15(sheetPIK)}:M{ffcwp.ffcwpend(sheetPIK)+20}')
            data31JUNE = sheetJUNE.get(
                f'A{ffcwp.ffcwp15(sheetJUNE)}:M{ffcwp.ffcwpend(sheetJUNE)+20}')
            data31LM = sheetLM.get(
                f'A{ffcwp.ffcwp15(sheetLM)}:M{ffcwp.ffcwpend(sheetLM)+20}')
            return data31KOMENDA, data31PIK, data31LM, data31JUNE

        return None
