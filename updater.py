import gspread
from datetime import datetime
from FFCWP import ffcwp


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
    sheetweneed = None  # Initialize sheetweneed here

    def __init__(self, config):
        self.client = config['client']
        self.sheetPIK = config['sheetPIK']
        self.sheetJUN = config['sheetJUN']
        self.sheetLM = config['sheetLM']
        self.ui = config['ui']
        self.sheetwages = config['sheetWAGES']
        self.employee_list = None
        self.adress = None
        self.today_date = datetime.now()

    def getCellAddrToday(self, sheetweneed):
        # Format the date as "01.03.2025" to match the cell content
        formatted_date = self.today_date.strftime("%d.%m.%Y")
        addr = ffcwp.find_first_matching_cell(
            sheetweneed, date=[formatted_date])
        return addr

    def get_last_item(self, lst):
        last_item = lst[-1] if lst else None
        print(
            f"Last item in employee list: {last_item} and type is {type(last_item)}")
        if last_item == 'Июнь':
            return self.sheetJUNE
        elif last_item == 'Пик':
            return self.sheetPIK
        elif last_item == 'Лондон молл':
            return self.sheetLM
        else:
            return None

    def _update_emp(self):
        """
        Requests an update to the Google Sheet with the provided employee data.

        Args:
            sheet_id (str): The ID of the sheet to update.
            employee_list (list): A list of employee data, where each employee is represented as a list
                                  containing name, role, and hours.

        Returns:
            dict: A dictionary containing the sheet ID, employee list, and address for the update.
        """
        Updater.sheetweneed = self.get_last_item(self.employee_list)
        if Updater.sheetweneed is None:
            raise ValueError(
                "No valid sheet selected. Check employee list or sheet mapping.")
        print(Updater.sheetweneed)
        adress = self.getCellAddrToday(Updater.sheetweneed)
        self.employee_list = self.ui.employee_request
        self.update_sheet_wEmp(Updater.sheetweneed, self.employee_list, adress)

    def update_sheet_wEmp(self, sheet_we_need, employee_list, adress):
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

        sheet = sheet_we_need
        print(f"{current_month}25")
        # Prepare the text to write
        text = "На смене: "

        for emp in employee_list:
            if isinstance(emp, list) and len(emp) == 3:
                name = emp[0]
                if name == "Пропуск" or name == "Выберете сотрудника":
                    continue
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
                text += f"{name}({hours};{role_letter}) "

                # Remove the trailing comma and space
        text = text.rstrip(" ")
        print(f"Updating sheet at address: {adress} with text: {text}")
        # Write the text to the specified cell address
        sheet.update(adress, [[text]])

    def add_new_sell(self, sheet_we_need, adress, payment_request):
        """
        Adds a new sell entry to the specified Google Sheet with employee shift information and payment details.

        Args:
            sheet_we_need (str): The ID of the sheet to update.
            employee_list (list): A list of employee data, where each employee is represented as a list
                                  containing name, role, and hours.
            adress (str): The cell address where the text should be written.
            payment_request (dict): A dictionary containing payment details to be added to the sheet.
        """
        # Prepare the text to write for employee sales
        text = "Продажи: "
        # Remove the trailing space
        text = text.rstrip(" ")

        # Write the text to the specified cell address
        sheet_we_need.update(adress, [[text]])

        # Extract payment details and write them to the same row as the address
        payment_details = [
            str(payment_request.get('Тип товара', '')) +
            ', ' + str(payment_request.get('Товар', '')),
            str(payment_request.get('Время чека', '')),
            str(payment_request.get('Количество человек', '')),
            str(payment_request.get('По карте', '')),
            str(payment_request.get('Наличные', '')),
            str(payment_request.get('НП', '')),
            str(payment_request.get('QR', '')),
            str(payment_request.get('Способ оплаты', '')),
            str(payment_request.get('Тип оплаты', '')),
            str(payment_request.get('Дата', '')),
            str(payment_request.get('Проценты', '')),

        ]

        # Determine the row number from the address
        row_number = int(''.join(filter(str.isdigit, adress)))
        print(
            f"Adding payment details at row: {row_number} with details: {payment_details}")
        # Write the payment details to the same row, starting from the next column
        # Batch update to work around Google API limitations
        updates = []
        # Start from column B (2)
        for col, detail in enumerate(payment_details, start=2):
            # Convert column number to letter
            cell_address = f"{chr(64 + col)}{row_number}"
            updates.append({'range': cell_address, 'values': [[detail]]})

        # Perform batch update
        body = {'data': updates, 'valueInputOption': 'USER_ENTERED'}
        sheet_we_need.batch_update(body)
