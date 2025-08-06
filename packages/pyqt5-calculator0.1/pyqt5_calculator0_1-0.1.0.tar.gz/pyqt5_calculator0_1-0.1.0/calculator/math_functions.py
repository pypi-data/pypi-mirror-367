def add(a, b):
  return a + b

def subtract(a, b):
  return a - b

def multiply(a, b):
  return a * b

def divide(a, b):
  return a / b if b != 0 else "Division by zero are not allowed"

def power(a):
  try:
    a = float(a)
    a =  a**2
    return str(a)
  except ValueError:
    return a

def sqrt(a):
  try:
    a = float(a)
    if a >= 0:
      a = a ** 0.5
      return str(a)
    else:
      return None
  except ValueError:
    return a

def percentage(a):
  try:
    a = float(a)
    a = a / 100
    return str(a)
  except ValueError:
    return a

def plus_minus(a):
  try:
    a = float(a)
    a = -a
    return str(a)
  except ValueError:
    return a

def del_symbol(a):
  return (a[:len(a) - 1])

def del_all_symbols(a):
  return (a[0:0])
