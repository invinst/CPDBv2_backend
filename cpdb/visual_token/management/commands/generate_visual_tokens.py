from django.conf import settings
from django.core.management.base import BaseCommand

import tqdm

from data.models import Officer
from visual_token.engine import open_engine
from visual_token.renderers import OfficerSocialGraphVisualTokenRenderer
from visual_token.utils import clear_folder


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_folder(settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER)
        renderer = OfficerSocialGraphVisualTokenRenderer()
        with open_engine(renderer) as engine:
            for officer in tqdm(Officer.objects.all()):
                engine.generate_visual_token(officer)
