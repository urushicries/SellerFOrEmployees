class Controller:
    def __init__(self, updater, model, ui):
        self.updater = updater
        self.model = model
        self.ui = ui
    def handle_employee_data(employee_data):
        # Example: send employee data to updater
        self.updater.update_employee(employee_data)

    def handle_sale_data(sale_data):
        # Example: send sale data to updater
        self.updater.update_sale(sale_data)

    def handle_shift_close():
        # Example: trigger shift close in updater
        self.updater.close_shift()

    def validate_login(self):
        return self.model.validate_login(self.ui.username_var.get(), self.ui.password_var.get())


