import pandas

def getAdsData(filepath):
    df = pandas.read_csv(filepath)
    return df
