
def string_to_float(_str):
    if isinstance(_str, (int, float)):
        return _str
    res = float(_str.replace(',',''))
    return res

def string_to_int(_str):
    if isinstance(_str, (int, float)):
        return _str
    res = int(_str.replace(',',''))
    return res

def percent_to_float(_str):
    if isinstance(_str, (int, float)):
        return _str
    s = _str.strip('%')
    return string_to_float(s)

def dollar_to_float(_str):
    if isinstance(_str, (int, float)):
        return _str
    res = float(_str.replace('$',''))
    return res
