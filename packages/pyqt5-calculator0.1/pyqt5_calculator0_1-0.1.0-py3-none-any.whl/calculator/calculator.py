from math_functions import *
from history import *
from validation import *

def calculator(num1, act, num2):
  operations = history_load()
  num1 = check_number(num1)
  act = check_action(act)
  num2 = check_number(num2)

  result = None
  if num1 != None and num2 != None:
    if act == '+':
      result = add(num1, num2)

    elif act == '-':
      result = subtract(num1, num2)

    elif act == '*':
      result = multiply(num1, num2)

    elif act == '/':
      try:
        result = divide(num1, num2)
      except ZeroDivisionError:
        return None

    elif act == '**':
      result = power(num1, num2)

    elif num1[-1] == '%':
      num1 = percentage(num1)

    elif num2[-1] == '%':
      num2 = percentage(num2)


    entry = f"{num1} {act} {num2} = {result}"
    operations.append(entry)
    history_save(operations)
    return entry

