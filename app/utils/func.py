
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
    _str = removeAllSpace(_str)
    params = _str.split('-')
    return (params[0], params[1])