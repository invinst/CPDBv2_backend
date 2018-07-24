from django.conf import settings
from django.core.management.base import BaseCommand

import moviepy.editor as mpy

from visual_token.renderer import make_draw_frame
from visual_token.utils import clear_folder
from officers.doc_types import OfficerInfoDocType


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_folder(settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER)
        fps = 40
        frame_per_year = 20

        for officer in OfficerInfoDocType().search().query(
                'bool',
                should=[
                    {'range': {'allegation_count': {'gt': 0}}},
                    {'range': {'trr_count': {'gt': 0}}}
                ]).scan():
            officer_dict = officer.to_dict()
            officer_percentiles = officer_dict.get('percentiles', [])
            if len(officer_percentiles) > 0:
                chart_data = [
                    {
                        'percentile_allegation_civilian': float(data['percentile_allegation_civilian']),
                        'percentile_allegation_internal': float(data['percentile_allegation_internal']),
                        'percentile_trr': float(data['percentile_trr'])
                    }
                    for data in officer_percentiles
                ]

                duration = float(frame_per_year) * (len(chart_data) - 1) / fps
                clip = mpy.VideoClip(
                    make_draw_frame(chart_data, duration),
                    duration=duration
                )
                clip.write_videofile(
                    '%s/officer_%s.mp4' % (settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER, officer_dict['id']),
                    fps=fps
                )
