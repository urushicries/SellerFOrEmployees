import gspread
from datetime import datetime


class Updater:
    """
    Updater class is responsible for managing and updating Google Sheets with employee shift information.
    Attributes:
        client (object): The Google Sheets client used to interact with the API.
        shtKOM_id (str): The ID of the KOM sheet.
        shtPIK_id (str): The ID of the PIK sheet.
        shtJUN_id (str): The ID of the JUN sheet.
        shtLM_id (str): The ID of the LM sheet.
        sheetKOM (object): The KOM sheet object (initialized later).
        sheetPIK (object): The PIK sheet object (initialized later).
        sheetJUNE (object): The JUNE sheet object (initialized later).
        sheetLM (object): The LM sheet object (initialized later).
    Methods:
        (None explicitly defined in the provided code snippet, but the class appears to handle opening
        sheets, preparing text based on employee data, and updating specific cells in the sheet.)
    """

    def __init__(self, config):
        self.client = config['client']
        self.shtKOM_id = config['shtKOM_id']
        self.shtPIK_id = config['shtPIK_id']
        self.shtJUN_id = config['shtJUN_id']
        self.shtLM_id = config['shtLM_id']

        self.sheetKOM = None
        self.sheetPIK = None
        self.sheetJUNE = None
        self.sheetLM = None

    def get_last_item(self, lst):
        """
        Returns the last item of a list.

        Args:
            lst (list): The list from which to extract the last item.

        Returns:
            object: The last item of the list, or None if the list is empty.
        """
        last_item = lst[-1] if lst else None
        if last_item == 'Июнь':
            self.sheetJUNE = self.client.open_by_key(
                self.shtJUN_id)
        elif last_item == 'ПИК':
            self.sheetPIK = self.client.open_by_key(
                self.shtPIK_id)
        elif last_item == 'Лондон':
            self.sheetPIK = self.client.open_by_key(
                self.shtPIK_id)

    def update_sheet(self, sheet_we_need, employee_list, adress):
        """
        Updates the specified Google Sheet with employee shift information.

        Args:
            sheet_we_need (str): The ID of the sheet to update.
            employee_list (list): A list of employee data, where each employee is represented as a list
                                  containing name, role, and hours.
            adress (str): The cell address where the text should be written.
        """
        # Open the sheet using the client and sheet ID
        # Get the current month name
        months = {
            "January": "Январь", "February": "Февраль", "March": "Март", "April": "Апрель",
            "May": "Май", "June": "Июнь", "July": "Июль", "August": "Август",
            "September": "Сентябрь", "October": "Октябрь", "November": "Ноябрь", "December": "Декабрь"
        }
        current_month = months[datetime.now().strftime("%B")]

        sheet = self.client.open_by_key(
            sheet_we_need).worksheet(f"{current_month}25")
        print(f"{current_month}25")
        # Prepare the text to write
        text = "На смене: "
        for emp in employee_list:
            if isinstance(emp, list) and len(emp) == 3:
                name = emp[0]
                role = emp[1]
                hours = emp[2]
                if "Оператор" in role:
                    role_letter = "О"
                elif "Администратор" in role:
                    role_letter = "А"
                elif "стажер" in role:
                    role_letter = "С"
                else:
                    role_letter = ""
                text += f"{name} ({hours}, {role_letter}), "

                # Remove the trailing comma and space
        text = text.rstrip(", ")

        # Write the text to the specified cell address
        sheet.update(adress, text)
