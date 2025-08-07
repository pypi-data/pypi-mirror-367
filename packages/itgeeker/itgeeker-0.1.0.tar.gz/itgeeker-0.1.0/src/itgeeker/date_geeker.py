# -*- coding: utf-8 -*-

import datetime

def is_summer_vacation(date=None):
    if date is None:
        date = datetime.date.today()
    year = date.year
    start = datetime.date(year, 7, 1)
    end = datetime.date(year, 9, 30)
    return start <= date <= end