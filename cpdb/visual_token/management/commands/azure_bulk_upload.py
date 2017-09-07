from subprocess import Popen

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        Popen([
            'blobxfer', settings.VISUAL_TOKEN_STORAGEACCOUNTNAME, 'visual-token',
            './',
            '--upload', '--include', '*.png', '--no-recursive'],
            cwd=settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER).wait()
