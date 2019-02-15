from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Q

from tqdm import tqdm

from data.models import AttachmentFile
from analytics.ga_utils import initialize_analyticsreporting, extract_report_rows, get_ga_report_response


class Command(BaseCommand):
    help = "Update attachment file views count from GA events"

    def get_ga_attachment_click_events(self):
        analytics = initialize_analyticsreporting()
        page_token = None
        while True:
            response = get_ga_report_response(
                analytics,
                {
                    "viewId": settings.GOOGLE_ANALYTICS_VIEW_ID,
                    "dateRanges": [
                        {
                            "startDate": "2018-01-01",
                            "endDate": datetime.now().strftime('%Y-%m-%d')
                        }
                    ],
                    "dimensions": [
                        {
                            "name": "ga:eventLabel"
                        }
                    ],
                    "metrics": [
                        {
                            "expression": "ga:totalEvents"
                        }
                    ],
                    "filtersExpression": "ga:eventCategory==attachment_click"
                },
                page_token)
            report = response['reports'][0]
            for row in extract_report_rows(report):
                yield row
            page_token = report.get('nextPageToken', None)
            if page_token is None:
                break

    def valid_event(self, event):
        return 'Target URL: https' in event['ga:eventLabel']

    def extract_url_and_count(self, event):
        count = int(event['ga:totalEvents'])
        search_str = 'Target URL: '
        ind = event['ga:eventLabel'].index(search_str) + len(search_str)
        return event['ga:eventLabel'][ind:], count

    def handle(self, *args, **kwargs):
        for event in tqdm(self.get_ga_attachment_click_events(), desc='Process event'):
            if not self.valid_event(event):
                continue
            url, count = self.extract_url_and_count(event)
            AttachmentFile.objects.filter(Q(url=url) | Q(original_url=url)).update(views_count=count)
