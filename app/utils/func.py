import datetime

def removeAllSpace(_str):
    _str = _str.replace(' ', '')
    return _str

def removeSigns(_str):
    _str = _str.replace(',','')
    _str = _str.replace('%', '')
    _str = _str.replace('$','')
    return _str

def str_to_float(_str):
    if isinstance(_str, (int, float)):
        return _str
    if _str == '' or _str is None:
        return 0

    return float(removeSigns(_str))

def str_to_int(_str):
    if isinstance(_str, (int, float)):
        return _str

    if _str == '' or _str is None:
        return 0

    removeSigns(_str)
    return int(_str)

def getStartEndDate(_str):
    if len(_str) < 2:
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=365)

        # if _str == 0:
        #     start_date = end_date - datetime.timedelta(days=7)
        # if _str == 1:
        #     start_date = end_date - datetime.timedelta(days=28)
        if _str < 2:
            start_date = end_date - datetime.timedelta(days=90)
        if _str == 3:
            start_date = end_date - datetime.timedelta(days=180)
        if _str == 4:
            start_date = end_date - datetime.timedelta(days=365)
        if _str == 5:
            start_date = end_date - datetime.timedelta(days=480)

        start = start_date.strftime("%m/%d/%Y")
        end = end_date.strftime("%m/%d/%Y")

        return (start, end)

    _str = removeAllSpace(_str)

    params = _str.split('-')

    return (params[0], params[1])