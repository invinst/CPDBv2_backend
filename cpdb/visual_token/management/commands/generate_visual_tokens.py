from django.conf import settings
from django.core.management.base import BaseCommand


from visual_token.writers import FFMpegWriter
from visual_token.figures import draw_frame
from visual_token.utils import clear_folder


class Command(BaseCommand):

    def handle(self, *args, **options):
        clear_folder(settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER)
        width = 640
        height = 640
        writer = FFMpegWriter(width, height)
        writer.run(draw_frame, frame_count=200, out_path='%s/out.mp4' % settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER)
