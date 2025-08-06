def check_number(num):
  if num.strip() == '':
    return None
  elif num[-1] == '%':
    try:
      num = num.replace('%', '')
      return percentage(float(num))
    except ValueError:
      return None
  elif num[-1] == 'v':
    try:
      num = num.replace('v', '')
      return sqrt(float(num))
    except ValueError:
      return None
  else:
    try:
      num = float(num)
      return num
    except ValueError:
      return None

def check_action(act):
  symbols = ['**', '+', '-', '/', 'q','*']
  if act in symbols:
    return act
  else:
    return None