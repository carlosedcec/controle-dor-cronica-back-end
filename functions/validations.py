import re
from datetime import datetime

class ValidationsHelper():

    def is_valid_date(date):

        # verifica se a data esta no formato adequado, senão retorna false
        dateReg = r"^\d{4}[-]\d{2}[-]\d{2}$"
        if not re.fullmatch(dateReg, date):
            return False
        
        # testa se é uma data válida e retorna true ou false
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def is_valid_time(time):

        # verifica se a hora esta no formato adequado, senão retorna false
        timeReg = r"^\d{2}[:]\d{2}$"
        if not re.fullmatch(timeReg, time):
            return False
        
        # testa se é uma hora válida e retorna true ou false
        try:
            datetime.strptime(time, "%H:%M")
            return True
        except ValueError:
            return False