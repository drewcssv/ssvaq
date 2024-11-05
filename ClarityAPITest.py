from time import sleep
import requests

clarity_api_key = 'u7JGpnsQK9pM6XO52v5gxiP63j7EYUTw0nZzMsk5'
clarity_api_base_url = 'https://clarity-data-api.clarity.io'

def request_and_fetch_a_report():
    headers = {"x-api-key": clarity_api_key}

    # request the report
    result = requests.post(url=clarity_api_base_url + "/v2/report-requests",
                           headers=headers,
                           json={
                               "org": "acterra",
                               "report": "datasource-measurements",
                               "datasourceIds": ["DUQNX2363","DUQNX2363"],
                               "outputFrequency": "hour",
                               "startTime": "2024-07-01T01:00:00.000Z",
                               "endTime": "2024-08-17T01:00:00.000Z",
                           })
    result.raise_for_status()
    result_json = result.json()
    reportId = result_json['reportId']

    # poll for its completion
    for i in range(12):
        print("sleeping 1 minute")
        sleep(60)
        print("fetching report status ... ", end="")
        statusUrl = clarity_api_base_url + f"/v2/report-requests/{reportId}"
        result = requests.get(url=statusUrl, headers=headers)
        result.raise_for_status()
        result_json = result.json()
        print(result_json.get("reportStatus"))
        if result_json.get("reportStatus") != 'in-progress':
            break

    print(result_json)

    if result_json.get("reportStatus") == 'succeeded':
        # if it succeeded, fetch the resulting files
        for i, url in enumerate(result_json['urls']):
            with requests.get(url=url, stream=True) as result:
                result.raise_for_status()
                filename = f"extract_{i}.csv"
                # stream to disk
                with open(f"{filename}", "w") as f:
                    for chunk in result.iter_content(1024 * 1024, decode_unicode=True):
                        f.write(chunk)


if __name__ == "__main__":
    request_and_fetch_a_report()