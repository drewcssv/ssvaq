# simple demo using Clarity Data API

import requests
import os
import csv
import pprint
import datetime


BASEURL = 'https://clarity-data-api.clarity.io'
HEADERS = {
    'Accept-Encoding': 'gzip',
   # 'x-api-key': os.environ.get('u7JGpnsQK9pM6XO52v5gxiP63j7EYUTw0nZzMsk5') # put your key in the environment or directly here
   'x-api-key': 'u7JGpnsQK9pM6XO52v5gxiP63j7EYUTw0nZzMsk5' # put your key in the environment or directly here !!! EST
}


def check_can_connect():
    # verify can reach the API
    response = requests.get(BASEURL, HEADERS)
    http_code = response.status_code
    connected = (http_code == 200)
    if connected:
        print('Connected to Clarity')
    else:
        print(f'{http_code}  :(  Cannot connect')


def get_recent_measurements(org, datasource_ids, output_frequency, format, metric_selector):
    # Fetch measurements from the API
    url = BASEURL + '/v2/recent-datasource-measurements-query'
    request_body = {
        'org': org,
        'datasourceIds': datasource_ids,
        'outputFrequency': output_frequency,
        'format': format,
        'metricSelect': metric_selector
    }
    response = requests.post(url, headers=HEADERS, json=request_body)
    response.raise_for_status()
    return response.text


def csv_to_typed(csv_data, fields_to_extract):
    # slice specific columns out of the CSV-style response
    # convert each to best Python type
    # return dictionary

    def convert_to_best_type(value):
        # Try these types in order: float, datetime, else string
        try:
            return float(value)
        except Exception:
            try:
                return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
            except Exception:
                return value

    reader = csv.DictReader(csv_data.splitlines())
    return [{field: convert_to_best_type(row[field]) for field in fields_to_extract} for row in reader]


check_can_connect()

tabular = get_recent_measurements(
        org='acterra',
        datasource_ids=['DUQNX2363'],
        format='csv-wide',
        output_frequency='hour',
        metric_selector='only pm2_5ConcMass1HourMean'
    )

measurements = csv_to_typed(tabular, [
        'startOfPeriod',
        'pm2_5ConcMass1HourMean.value',
        'pm2_5ConcMass1HourMean.status'
    ])

pprint.pprint(measurements)