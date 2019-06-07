# /app/googleads/controller.py

from googleads import adwords

from .models import GoogleAdwords
from app.auth import google_auth
from app.db import db
from datetime import datetime
from app.utils import func
import io
import sys
import pandas as pd
from app.googlesc import GoogleSearchConsole

def getData(project_id):
    return GoogleAdwords.query.filter_by(project_id=project_id).all()

def deleteAll(project_id):
    GoogleAdwords.query.filter_by(project_id=project_id).delete()

def pull_adwords_data(client, start_date, end_date):

    start_date = datetime.strptime(start_date, "%m/%d/%Y")
    end_date = datetime.strptime(end_date, "%m/%d/%Y")
    start_date = start_date.strftime("%Y%m%d")
    end_date = end_date.strftime("%Y%m%d")

    output = io.StringIO()

    report_downloader = client.GetReportDownloader(version='v201809')
    report_query = (adwords.ReportQueryBuilder()
        .Select('Query', 'Conversions', 'ValuePerConversion', 'ConversionRate', 'AverageCpc')
        .From('SEARCH_QUERY_PERFORMANCE_REPORT')
        .During(None, start_date, end_date)
        .Build())

    report = report_downloader.DownloadReportWithAwql(report_query, 'CSV', output, skip_report_header=True,
              skip_column_header=False, skip_report_summary=True)

    output.seek(0)

    df = pd.read_csv(output)
    df.head()

    return df

def store_adwords(client, project_id, start_date, end_date):
    GoogleAdwords.query.filter_by(project_id=project_id).delete()

    report = pull_adwords_data(client, start_date, end_date)

    for index, row in report.iterrows():
        insert_row(project_id, row)

def insert_row(id, row):
    item = GoogleAdwords(
        search_terms = row['Search term'],
        conversions = row['Conversions'],
        conversion_value = func.str_to_float(row['Value / conv.']),
        conversion_rate = func.str_to_float(row['Conv. rate']),
        avg_cpc = func.str_to_float(row['Avg. CPC']) / 1000000.0,
        project_id = id
    )
    db.session.add(item)
    db.session.commit()
