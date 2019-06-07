# /app/googlesc/controller.py

import os
import logging
import csv
import json
import time
import sys
from datetime import datetime, timedelta
import itertools
import argparse
from collections import OrderedDict
from googleapiclient.errors import HttpError

from .models import GoogleSearchConsole
from app.auth import google_auth
from app.db import db

def get_property_urls(service):
    site_list = service.sites().list().execute()

    # Filter for verified websites
    verified_sites_urls = [s['siteUrl'] for s in site_list['siteEntry']
                       if s['permissionLevel'] != 'siteUnverifiedUser'
                          and s['siteUrl'][:4] == 'http']

    # Return the URLs of all websites you are verified for.
    return verified_sites_urls

def getData(project_id):
    return GoogleSearchConsole.query.filter_by(project_id = project_id).all()

def deleteAll(project_id):
    GoogleSearchConsole.query.filter_by(project_id = project_id).delete()

def pull_search_console_data(service, project, start_date, end_date, max_rows=25):
    start_date = datetime.strptime(start_date, "%m/%d/%Y")
    end_date = datetime.strptime(end_date, "%m/%d/%Y")
    request = {
        'startDate': start_date.strftime("%Y-%m-%d"),
        'endDate': end_date.strftime("%Y-%m-%d"),
        'dimensions': ['query', 'country'],
        'dimensionFilterGroups': [{
         'filters': [{
              'dimension': 'country',
              'operator': 'contains',
              'expression': project.country
          }]
        }],
        'rowlimit': max_rows
    }
    
    response = execute_request(service, project.property_url, request)

    return response

def store_data(service, project, start_date, end_date):
    # delete data in database
    GoogleSearchConsole.query.filter_by(project_id = project.id).delete()

    # pull data from google search console server
    response = pull_search_console_data(service, project, start_date, end_date)

    # save to database
    if 'rows' in response:
        for row in response['rows']:
            insert_row(row, project.id)

def insert_row(row, project_id):
    item = GoogleSearchConsole(row['keys'][0], row['position'], project_id)
    db.session.add(item)
    db.session.commit()

def execute_request(
    service,
    property_uri,
    request,
    max_retries=5,
    wait_interval=4,
    retry_errors=(
        503,
        500)):

    response = None
    retries = 0
    while retries <= max_retries:
        try:
            response = service.searchanalytics().query(
                siteUrl=property_uri, body=request).execute()
        except HttpError as err:
            decoded_error_body = err.content.decode('utf-8')
            json_error = json.loads(decoded_error_body)
            if json_error['error']['code'] in retry_errors:
                time.sleep(wait_interval)
                retries += 1
                continue
        break
    return response