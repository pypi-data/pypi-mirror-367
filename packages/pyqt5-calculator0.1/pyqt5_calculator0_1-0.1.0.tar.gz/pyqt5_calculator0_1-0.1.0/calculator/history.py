import json
import os

HISTORY_FILE = 'calculator_history.json'

def history_save(operations):
    with open(HISTORY_FILE, 'w') as file:
        json.dump(operations, file, indent=4)


def history_load():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r') as file:
      return json.load(file)

def history_show():
    if not os.path.exists(HISTORY_FILE):
      return []
    else:
      return history_load()

def history_clear():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'w') as file:
      json.dump([], file)
    return True