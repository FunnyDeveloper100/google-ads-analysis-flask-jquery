
def string_to_float(_str):
    res = float(_str.replace(',',''))
    return res

def string_to_int(_str):
    res = int(_str.replace(',',''))
    return res

def percent_to_float(_str):
    s = _str.strip('%')
    return float(s)

def dollar_to_float(_str):
    res = _str.replace('$','')
    return string_to_float(res)
