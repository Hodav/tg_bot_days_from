def join_date(dates, date):
    if dates:
        if dates.split(',')[-1] == date:
            return dates
        else:
            return dates + ',' + date
    return date