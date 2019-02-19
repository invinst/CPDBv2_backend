from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from django.conf import settings


def initialize_analyticsreporting():  # pragma: no cover
    """
    Initializes an Analytics Reporting API V4 service object.

    Returns:
        An authorized Analytics Reporting API V4 service object.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        settings.GOOGLE_APPLICATION_CREDENTIALS,
        ['https://www.googleapis.com/auth/analytics.readonly']
    )
    return build('analyticsreporting', 'v4', credentials=credentials)


def extract_report_rows(report):
    """
    Parses and extract rows from Analytics Reporting API V4 response.

    Args:
        report: An Analytics report from the response.
    Returns:
        generator that yield rows
    """
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

    for row in report.get('data', {}).get('rows', []):
        dimensions = row.get('dimensions', [])
        dateRangeValues = row.get('metrics', [])

        resulting_row = dict()

        for header, dimension in zip(dimensionHeaders, dimensions):
            resulting_row[header] = dimension

        for i, values in enumerate(dateRangeValues):
            for metricHeader, value in zip(metricHeaders, values.get('values')):
                resulting_row[metricHeader.get('name')] = value

        yield resulting_row


def get_ga_report_response(analytics, report_request_body, page_token=None):
    """Queries the Analytics Reporting API V4.

    Args:
        analytics: An authorized Analytics Reporting API V4 service object.
        report_request_body:
        page_token: used for pagination
    Returns:
        The Analytics Reporting API V4 response.
    """
    req_body = {
        "reportRequests": [report_request_body]
    }

    if page_token is not None:
        req_body["reportRequests"][0]["pageToken"] = page_token

    return analytics.reports().batchGet(body=req_body).execute()
