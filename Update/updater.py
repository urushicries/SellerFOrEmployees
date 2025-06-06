import gspread
from datetime import datetime
from Model.FFCWP import ffcwp
import pandas as pd


class Handler:
    def __init__(self, successor=None):
        self._successor = successor

    def handle(self, request_type, *args, **kwargs):
        handled = self._handle(request_type, *args, **kwargs)
        if not handled and self._successor:
            return self._successor.handle(request_type, *args, **kwargs)
        return handled

    def _handle(self, request_type, *args, **kwargs):
        raise NotImplementedError("Must implement _handle method")


class EmployeeHandler(Handler):
    def _handle(self, request_type, *args, **kwargs):
        if request_type == "employee":
            # args[0] is expected to be employee_list
            updater = kwargs.get('updater')
            if updater:
                updater._update_emp()
                return True
        return False


class SellHandler(Handler):
    def _handle(self, request_type, *args, **kwargs):
        if request_type == "sell":
            updater = kwargs.get('updater')
            payment_req = kwargs.get('payment_req')
            if updater and payment_req:
                updater.catch_req_sell(payment_req)
                return True
        return False


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
    sheetweneed = None
    current_row = 0

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Updater, cls).__new__(cls)
        return cls._instance

    def __init__(self, config):
        self.all_requests = pd.DataFrame(columns=[
            "Тип товара", "Товар", "Время чека", "Количество человек", "Карта",
            "QR/СБП", "Наличные по кассе", "НП", "Игра AW", "Стоимость",
            "Дата игры", "Время", "Тип оплаты", "Проценты"
        ])
        self.client = config['client']
        self.sheetPIK = config['sheetPIK']
        self.sheetJUN = config['sheetJUN']
        self.sheetLM = config['sheetLM']
        self.sheetKom = config['sheetKOM']
        self.ui = None
        self.sheetwages = config['sheetWAGES']
        self.employee_list = None
        self.adress = None
        self.today_date = datetime.now()
        self.current_row = 0

    def getCellAddrToday(self, sheetweneed):
        """
        Retrieves the address of the first cell in the given sheet that matches today's date.
        Args:
            sheetweneed (object): The sheet object to search for the date.
        Returns:
            str: The address of the first cell containing today's date in the format "DD.MM.YYYY".
        """

        # Format the date as "01.03.2025" to match the cell content
        formatted_date = self.today_date.strftime("%d.%m.%Y")
        addr = ffcwp.find_first_matching_cell(
            sheetweneed, date=[formatted_date])
        return addr

    def get_last_item(self, lst):
        """
        Retrieves the last item from a given list and returns a corresponding sheet attribute
        based on the item's value.
        Args:
            lst (list): The list from which the last item will be retrieved.
        Returns:
            object: The corresponding sheet attribute (e.g., self.sheetJUNE, self.sheetPIK,
                    self.sheetLM, self.sheetKom) if the last item matches a predefined value.
                    Returns None if the list is empty or the last item does not match any
                    predefined value.
        Notes:
            - Prints the last item in the list and its type for debugging purposes.
            - Predefined values and their corresponding sheet attributes:
                - 'Июнь' -> self.sheetJUNE
                - 'Пик' -> self.sheetPIK
                - 'Лондон молл' -> self.sheetLM
                - 'Коменда' -> self.sheetKom
        """

        last_item = lst[-1] if lst else None
        print(
            f"Last item in employee list: {last_item} and type is {type(last_item)}")
        if last_item == 'Июнь':
            return self.sheetJUNE
        elif last_item == 'Пик':
            return self.sheetPIK
        elif last_item == 'Лондон молл':
            return self.sheetLM
        elif last_item == 'Коменда':
            return self.sheetKom
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
       
        months = {
            "January": "Январь", "February": "Февраль", "March": "Март", "April": "Апрель",
            "May": "Май", "June": "Июнь", "July": "Июль", "August": "Август",
            "September": "Сентябрь", "October": "Октябрь", "November": "Ноябрь", "December": "Декабрь"
        }
        current_month = months[datetime.now().strftime("%B")]

        sheet = sheet_we_need
        print(f"{current_month}25")
       
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
                elif "Стажер" in role:
                    role_letter = "С"
                else:
                    role_letter = "С"
                text += f"{name}({hours};{role_letter}) "

        text = text.rstrip(" ")
        print(f"Updating sheet at address: {adress} with text: {text}")
      
        sheet.update(adress, [[text]])

    def catch_req_sell(self, payment_req):
        """
        Handles the process of recording a new sales request.
        This method takes a payment request and adds a new sales entry to the specified sheet.
        It determines the appropriate cell address for today's date and updates the sheet with
        the provided payment request details.
        Args:
            payment_req (str): The payment request details to be recorded.
        Returns:
            None
        """

        self.add_new_sell(sheet_we_need=Updater.sheetweneed,
                          adress=self.getCellAddrToday(Updater.sheetweneed), payment_request=payment_req)

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

     
        payment_details = [
            f"{payment_request.get('Тип товара', '')}, {payment_request.get('Товар', '')}",
            payment_request.get('Время чека', ''),
            payment_request.get('Количество человек', '1'),
            float(payment_request.get('Карта', '')),
            float(payment_request.get('QR/СБП', '')),
            float(payment_request.get('Наличные по кассе', '')),
            float(payment_request.get('НП', '')),
            float(payment_request.get('Игра AW', '')),
            '', '',
            payment_request.get('Комментарий', '')
        ]

        
        row_number = int(''.join(filter(str.isdigit, adress)))
        if Updater.current_row == 0:
            Updater.current_row = row_number + 1
        else:
            Updater.current_row += 1
        self.current_row = Updater.current_row

     
        updates = []

        if not hasattr(sheet_we_need, 'batch_update'):
            raise TypeError(
                "sheet_we_need must be a valid Google Sheets object, not a string.")

        columns = ['B', 'C', 'D', 'E', 'F', 'G', 'H',
                   'I', 'J', 'K', 'L'] 
        for col, detail in enumerate(payment_details, start=2):
            cell_address = f"{columns[col - 2]}{self.current_row}"
            updates.append({'range': cell_address, 'values': [[detail]]})

       
        new_entry = {
            "Тип товара": payment_request.get('Тип товара', ''),
            "Товар": payment_request.get('Товар', ''),
            "Время чека": payment_request.get('Время чека', ''),
            "Количество человек": payment_request.get('Количество человек', '1'),
            "Карта": float(payment_request.get('Карта', 0) or 0),
            "QR/СБП": float(payment_request.get('QR/СБП', 0) or 0),
            "Наличные по кассе": float(payment_request.get('Наличные по кассе', 0) or 0),
            "НП": float(payment_request.get('НП', 0) or 0),
            "Игра AW": float(payment_request.get('Игра AW', 0) or 0),
            "Стоимость": float(payment_request.get('Стоимость', 0) or 0),
            "Дата игры": payment_request.get('Дата игры', 'Сегодня'),
            "Время": payment_request.get('Время', ''),
            "Тип оплаты": payment_request.get('Тип оплаты', 'Полная оплата'),
            "Проценты": payment_request.get('Проценты', 0),
            "Комментарий": payment_request.get('Комментарий', '')
        }

        self.all_requests = pd.concat(
            [self.all_requests, pd.DataFrame([new_entry])], ignore_index=True)
        
        sheet_we_need.batch_update(updates)

    def setup_chain(self):
        self.chain = EmployeeHandler(SellHandler())

    def handle_request(self, request_type, **kwargs):
        if not hasattr(self, 'chain'):
            self.setup_chain()
        return self.chain.handle(request_type, updater=self, **kwargs)
