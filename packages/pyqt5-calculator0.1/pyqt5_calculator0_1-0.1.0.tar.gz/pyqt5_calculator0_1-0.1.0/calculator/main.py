import math_functions
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from ui.calculator_gui import Ui_MainWindow
from calculator import calculator
from history import history_show, history_clear
from validation import *
from math_functions import *
import os


class MyCalculator(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        with open(os.path.join(os.path.dirname(__file__), "styles", "style.qss"), "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        self.clear_on_next_input = False

        self.btn1.clicked.connect(lambda: self.add_to_display("1"))
        self.btn2.clicked.connect(lambda: self.add_to_display("2"))
        self.btn3.clicked.connect(lambda: self.add_to_display("3"))
        self.btn4.clicked.connect(lambda: self.add_to_display("4"))
        self.btn5.clicked.connect(lambda: self.add_to_display("5"))
        self.btn6.clicked.connect(lambda: self.add_to_display("6"))
        self.btn7.clicked.connect(lambda: self.add_to_display("7"))
        self.btn8.clicked.connect(lambda: self.add_to_display("8"))
        self.btn9.clicked.connect(lambda: self.add_to_display("9"))
        self.btn10.clicked.connect(lambda: self.add_to_display("0"))
        self.btn11.clicked.connect(lambda: self.add_to_display("."))
        self.btn12.clicked.connect(self.delete_all_text)
        self.btn13.clicked.connect(self.process_calculation)
        self.btn14.clicked.connect(lambda: self.add_to_display("+"))
        self.btn15.clicked.connect(lambda: self.add_to_display("-"))
        self.btn16.clicked.connect(lambda: self.add_to_display("*"))
        self.btn17.clicked.connect(lambda: self.add_to_display("/"))
        self.btn18.clicked.connect(self.press_sqrt)
        self.btn19.clicked.connect(self.power_by_two)
        self.btn20.clicked.connect(self.convert_to_percentage)
        self.btn21.clicked.connect(self.delete_symbol)
        self.btn22.clicked.connect(self.close_window)
        self.btn23.clicked.connect(self.positive_negative)
        self.actionShow_History.triggered.connect(self.open_history_window)
        self.actionShow_History.setShortcut("Ctrl+J")
        self.actionClear_History.triggered.connect(self.clear_history_window)
        self.actionClear_History.setShortcut("Ctrl+H")
        self.actionAbout.triggered.connect(self.open_about)
        self.actionAbout.setShortcut("Ctrl+I")

    def add_to_display(self, value):
        if self.clear_on_next_input:
            self.clear_screen_for_new_input()
            self.clear_on_next_input = False

        current_text = self.Screen.toPlainText() # paima esamą tekstą iš QTextEdit
        self.Screen.setPlainText(current_text + value)

    def clear_screen_for_new_input(self):
        self.Screen.setPlainText("")


    def open_about(self):
        QMessageBox.information(self, 'Inormation about Calculator v0.1', 'This calculator is developed using Python and the PyQt5 graphical user interface. \nFeatures:\nBasic arithmetic: addition, subtraction, multiplication, division \nPercentage calculation \nSquare root extraction \nChange number sign (+/-) \nExponentiation \nView and clear calculation history \nCreated for learning purposes.')

    def clear_history_window(self):
        history_clear()
        QMessageBox.information(self, 'History', 'History was deleted')


    def open_history_window(self):
        history_data = history_show()

        if not history_data:
            QMessageBox.warning(self, 'Warning', "No history data")
        else:
            history_text = "\n".join(history_data)
            QMessageBox.information(self, 'History', history_text)

    def close_window(self):
        self.close()

    def power_by_two(self):
        try:
            expression = self.Screen.toPlainText()
            num1, act, num2 = self.split_expression(expression)

            if num1 is None and act is None:
                num1 = expression
                squared = math_functions.power(num1)
                self.Screen.setPlainText(str(squared))

            elif act is None:
                squared = math_functions.power(num1)
                if squared is None:
                    QMessageBox.warning(self, 'Warning', "Squared action is invalid")
                else:
                    self.Screen.setPlainText(str(squared))

            elif num2 is None or num2 == "":
                squared = math_functions.power(num1)
                if squared is None:
                    QMessageBox.warning(self, 'Warning', "Squared action is invalid")
                else:
                    self.Screen.setPlainText(str(squared))

            else:
                squared = math_functions.power(num2)
                if squared is None:
                    QMessageBox.warning(self, 'Warning', "Squared action is invalid")
                else:
                    self.Screen.setPlainText(f"{num1}{act}{squared}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def positive_negative(self):
        try:
            expression = self.Screen.toPlainText()
            num1, act, num2 = self.split_expression(expression)

            if num1 is None and act is None:
                num1 = expression
                change_pos_neg = math_functions.plus_minus(num1)
                self.Screen.setPlainText(str(change_pos_neg))

            elif act is None:
                change_pos_neg = math_functions.plus_minus(num1)
                if change_pos_neg is None:
                    QMessageBox.warning(self, 'Warning', "Unable to change without a number")
                else:
                    self.Screen.setPlainText(str(change_pos_neg))

            elif num2 is None or num2 == "":
                change_pos_neg = math_functions.plus_minus(num1)
                if change_pos_neg is None:
                    QMessageBox.warning(self, 'Warning', "Unable to change without a number")
                else:
                    self.Screen.setPlainText(str(change_pos_neg))

            else:
                change_pos_neg = math_functions.plus_minus(num2)
                if change_pos_neg is None:
                    QMessageBox.warning(self, 'Warning', "Unable to change without a number")
                else:
                    self.Screen.setPlainText(f"{num1}{act}{change_pos_neg}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def convert_to_percentage(self):
        try:
            expression = self.Screen.toPlainText()
            num1, act, num2 = self.split_expression(expression)

            if num1 is None and act is None:
                num1 = expression
                percent_result = math_functions.percentage(num1)
                self.Screen.setPlainText(str(percent_result))

            elif act is None:
                percent_result = math_functions.percentage(num1)
                if percent_result is None:
                    QMessageBox.warning(self, 'Warning', 'Unable to calculate percentage')
                    return
                else:
                    self.Screen.setPlainText(str(percent_result))

            elif num2 is None or num2 == "":
                percent_result = math_functions.percentage(num1)
                if percent_result is None:
                    QMessageBox.warning(self, 'Warning', 'Unable to calculate percentage')
                    return
                else:
                    self.Screen.setPlainText(str(percent_result))

            else:
                percent_result = math_functions.percentage(num2)
                if percent_result is None:
                    QMessageBox.warning(self, 'Warning', 'Unable to calculate percentage')
                    return
                else:
                    self.Screen.setPlainText(f"{num1}{act}{percent_result}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def delete_symbol(self):
        try:
            expression = self.Screen.toPlainText()
            delete_one_symbol = math_functions.del_symbol(expression)
            self.Screen.setPlainText(delete_one_symbol)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_all_text(self):
        try:
            expression = self.Screen.toPlainText()
            delete_all = math_functions.del_all_symbols(expression)
            self.Screen.setPlainText(delete_all)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def press_sqrt(self):
        try:
            expression = self.Screen.toPlainText()
            num1, act, num2 = self.split_expression(expression)
            if num1 is None and act is None:
                num1 = expression
                sqrt_result = math_functions.sqrt(num1)
                self.Screen.setPlainText(str(sqrt_result))

            elif act is None:
                sqrt_result = math_functions.sqrt(num1)
                if sqrt_result is None:
                    QMessageBox.warning(self, "Warning", "Unable to calculate square root")
                    return
                else:
                    self.Screen.setPlainText(str(sqrt_result))

            elif num2 is None or num2 == "":
                sqrt_result = math_functions.sqrt(num1)
                if sqrt_result is None:
                    QMessageBox.warning(self, "Warning", "Unable to calculate square root")
                    return
                else:
                    self.Screen.setPlainText(str(sqrt_result))

            else:
                sqrt_result = math_functions.sqrt(num2)
                if sqrt_result is None:
                    QMessageBox.warning(self, "Warning", "Unable to calculate square root")
                    return
                else:
                    self.Screen.setPlainText(f"{num1}{act}{sqrt_result}")


        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def process_calculation(self):
        try:
            expression = self.Screen.toPlainText()

            num1, act, num2 = self.split_expression(expression)
            if not all([num1, act, num2]):
                QMessageBox.warning(self,"Warning", "Input is not valid")
                return

            result = calculator(num1, act, num2)

            if result is None:
                QMessageBox.warning(self, "Warning", "Input is not valid")
                return

            self.Screen.setPlainText(str(result))
            self.clear_on_next_input = True

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def split_expression(self, expr):
      for symbol in ['**', '+', '-',  '/', '*']:
        if symbol in expr:
          valid_symbol = check_action(symbol)
          if valid_symbol != None:
            parts = expr.split(valid_symbol, 1)
            return parts[0], valid_symbol, parts[1]
      return None, None, None


if __name__ == "__main__":
    app = QApplication([])
    window = MyCalculator()
    window.show()
    app.exec_()
