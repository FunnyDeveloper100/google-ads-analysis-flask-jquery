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


def rate_limit(max_per_minute):
    """
    Decorator function to prevent more than x calls per minute of any function
    Args:
        max_per_minute. Numeric type.
        The maximum number of times the function should run per minute.
    """
    min_interval = 60.0 / float(max_per_minute)

    def decorate(func):
        last_time_called = [0.0]

        def rate_limited_function(*args, **kwargs):
            elapsed = time.clock() - last_time_called[0]
            wait_for = min_interval - elapsed
            if wait_for > 0:
                time.sleep(wait_for)
            ret = func(*args, **kwargs)
            last_time_called[0] = time.clock()
            return ret
        return rate_limited_function
    return decorate


def date_range(start_date, end_date, delta=timedelta(days=1)):
    """
    Yields a stream of datetime objects, for all days within a range.
    The range is inclusive, so both start_date and end_date will be returned,
    as well as all dates in between.
    Args:
        start_date: The datetime object representing the first day in the range.
        end_date: The datetime object representing the second day in the range.
        delta: A datetime.timedelta instance, specifying the step interval. Defaults to one day.
    Yields:
        Each datetime object in the range.
    """
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += delta


def generate_filters(**kwargs):
    """
    Yields a filter list for each combination of the args provided.
    """
    kwargs = OrderedDict((k, v) for k, v in kwargs.items() if v)
    dimensions = kwargs.keys()
    values = list(kwargs.values())
    for vals in itertools.product(*values):
        yield [{
            'dimension': dim,
            'operator': 'equals',
            'expression': val} for dim, val in zip(dimensions, vals)
              ]


@rate_limit(200)
def execute_request(service, property_uri, request, max_retries=5, wait_interval=4,
                    retry_errors=(503, 500)):
    """
    Executes a searchanalytics request.
    Args:
        service: The webmasters service object/client to use for execution.
        property_uri: Matches the URI in Google Search Console.
        request: The request to be executed.
        max_retries. Optional. Sets the maximum number of retry attempts.
        wait_interval. Optional. Sets the number of seconds to wait between each retry attempt.
        retry_errors. Optional. Retry the request whenever these error codes are encountered.
    Returns:
        An array of response rows.
    """

    response = None
    retries = 0
    while retries <= max_retries:
        try:
            response = service.searchanalytics().query(siteUrl=property_uri, body=request).execute()
        except HttpError as err:
            decoded_error_body = err.content.decode('utf-8')
            json_error = json.loads(decoded_error_body)
            if json_error['error']['code'] in retry_errors:
                time.sleep(wait_interval)
                retries += 1
                continue
        break
    return response


def get_search_terms(service, property_uri, devices=['mobile', 'desktop', 'tablet'], url_type="", countries=[], max_rows_per_day=100, pages=[]):
    start_date = datetime.strptime("2019-01-01", "%Y-%m-%d")
    end_date = datetime.strptime("2019-05-01", "%Y-%m-%d")

    for day in date_range(start_date, end_date):
        output_file = os.path.join(
            "",
            "{}_{}.csv".format(url_type, day.strftime("%Y%m%d"))
        )
        day = day.strftime("%Y-%m-%d")
        output_rows = []

        for filter_set in generate_filters(
                page=pages,
                device=devices,
                country=countries):

            request = {
                'startDate': day,
                'endDate': day,
                'dimensions': ['query'],
                'rowLimit': max_rows_per_day,
                'dimensionFilterGroups': [
                    {
                        "groupType": "and",
                        "filters": filter_set
                    }
                ]
            }

            response = execute_request(service, property_uri, request)

            if response is None:
                logging.error(
                    "Request failed %s", json.dumps(
                        request, indent=2))
                continue

            if 'rows' in response:

                if pages:
                    filters = [
                        pages[0],
                        'worldwide',
                        'all_devices',
                        url_type]
                else:
                    filters = [
                        'gsc_property',
                        'worldwide',
                        'all_devices',
                        url_type]

                filter_mapping = {'page': 0, 'country': 1, 'device': 2}
                for _filter in filter_set:
                    filters[filter_mapping[_filter['dimension']]
                            ] = _filter['expression']

                for row in response['rows']:
                    keys = ','.join(row['keys'])
                    output_row = [
                        keys,
                        row['clicks'],
                        row['impressions'],
                        row['ctr'],
                        row['position']]
                    output_row.extend(filters)
                    output_rows.append(output_row)

        with open(output_file, 'w', newline="", encoding="utf-8-sig") as file_handle:  # noqa
            csvwriter = csv.writer(file_handle)
            csvwriter.writerows(output_rows)

        logging.info("Query for %s complete", day)


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
