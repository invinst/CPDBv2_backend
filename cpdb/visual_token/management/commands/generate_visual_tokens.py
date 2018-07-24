from django.conf import settings
from django.core.management.base import BaseCommand

from tqdm import tqdm

from visual_token.figures import ChartFigure
from visual_token.utils import clear_folder
from officers.doc_types import OfficerInfoDocType


PERCENTILE_KEYS = [
    'percentile_allegation_civilian', 'percentile_allegation_internal', 'percentile_trr'
]
CHART_DIMENSIONS = (640, 640)


class Command(BaseCommand):
    def has_enough_data(self, data):
        vals = [
            float(data.get(key, 0))
            for key in PERCENTILE_KEYS
        ]
        vals = [
            val for val in vals
            if val > 0
        ]
        return len(vals) >= 2

    def handle(self, *args, **options):
        clear_folder(settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER)
        figure = ChartFigure(*CHART_DIMENSIONS)

        query = OfficerInfoDocType().search().query(
            'bool',
            should=[
                {'range': {'allegation_count': {'gt': 0}}},
                {'range': {'trr_count': {'gt': 0}}}
            ])
        pbar = tqdm(total=query.count())
        for officer in query.scan():
            officer_dict = officer.to_dict()
            officer_percentiles = officer_dict.get('percentiles', [])
            pbar.update()

            chart_data = [
                [
                    float(data.get(key, 0))
                    for key in PERCENTILE_KEYS
                ]
                for data in officer_percentiles
                if self.has_enough_data(data)
            ]
            if len(chart_data) == 0:
                continue

            surface = figure.draw(chart_data[-1])
            surface.write_to_png(
                '%s/officer_%s.png' % (settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER, officer_dict['id']))
