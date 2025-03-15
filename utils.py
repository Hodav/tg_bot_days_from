from datetime import date

def join_date(dates:str, date:str):
    if dates:
        if dates.split(',')[-1] == date:
            return dates
        else:
            return dates + ',' + date
    return date

def is_future(cur_date:date):
    return cur_date > date.today()
