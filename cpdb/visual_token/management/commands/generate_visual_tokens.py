from django.conf import settings
from django.core.management.base import BaseCommand


from visual_token.writers import FFMpegWriter
from visual_token.figures import draw_frame
from visual_token.utils import clear_folder
from officers.doc_types import OfficerInfoDocType
from officers.serializers.doc_serializers import OfficerYearlyPercentileSerializer


class Command(BaseCommand):

    def handle(self, *args, **options):
        clear_folder(settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER)
        width = 640
        height = 640

        writer = FFMpegWriter(width, height)

        for officer in OfficerInfoDocType().search().query('term', id='12074').scan():
            officer_dict = officer.to_dict()
            percentiles_data = officer_dict.get('percentiles', [])
            if len(percentiles_data) > 0:
                percentiles = [
                    {
                        'percentile_allegation_civilian': float(data['percentile_allegation_civilian']),
                        'percentile_allegation_internal': float(data['percentile_allegation_internal']),
                        'percentile_trr': float(data['percentile_trr'])
                    }
                    for data in percentiles_data
                ]

                writer.run(
                    draw_frame,
                    percentiles,
                    frame_count=20 * (len(percentiles) - 1),
                    out_path='%s/%s.mp4' % (settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER, officer_dict['id'])
                )
