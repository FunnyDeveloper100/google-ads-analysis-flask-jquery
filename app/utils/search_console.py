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


def get_search_terms(
    service,
    property_uri,
    start_date,
    end_date,
    country="world wide",
    max_rows=2500,
    pages=[]):

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    request = {
        'startDate': start_date.strftime("%Y-%m-%d"),
        'endDate': end_date.strftime("%Y-%m-%d"),
        'dimensions': ['query'],
        'rowLimit': max_rows,
        'dimensionFilterGroups': [
            {
                'dimention': 'country',
                'expression': country
            }
        ]
    }

    response = execute_request(service, property_uri, request)

    return response


def get_sitemaps(webmasters_service):
    # Retrieve list of properties in account
    site_list = webmasters_service.sites().list().execute()

    # Filter for verified websites
    verified_sites_urls = [s['siteUrl'] for s in site_list['siteEntry']
                           if s['permissionLevel'] != 'siteUnverifiedUser'
                           and s['siteUrl'][:4] == 'http']

    # Printing the URLs of all websites you are verified for.
    for site_url in verified_sites_urls:
        print(site_url)
    # Retrieve list of sitemaps submitted
    sitemaps = webmasters_service.sitemaps().list(siteUrl=site_url).execute()
    if 'sitemap' in sitemaps:
        sitemap_urls = [s['path'] for s in sitemaps['sitemap']]
        print("  " + "\n  ".join(sitemap_urls))
