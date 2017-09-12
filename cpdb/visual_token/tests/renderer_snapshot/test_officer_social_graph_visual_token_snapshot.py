
from django.conf import settings

from snapshot_test.test import SnapshotTestMixin

from data.factories import OfficerFactory
from visual_token.renderers import OfficerSocialGraphVisualTokenRenderer
from .test import RendererSnapshotTestCase


def token_path(path):
    return '%s/%s' % (settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER, path)


class OfficerSocialGraphVisualTokenSnapshotTestCase(SnapshotTestMixin, RendererSnapshotTestCase):
    renderer_class = OfficerSocialGraphVisualTokenRenderer
    cleanupdirs = (settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER,)

    def test_single_officer(self):
        officer = OfficerFactory(first_name='John', last_name='Doe', id=1)
        self.engine.generate_visual_token(officer)
        self.assert_snapshot_match(token_path('officer_1.svg'), 'officer_1.svg')
        self.assert_snapshot_match(token_path('officer_1_facebook_share.png'), 'officer_1_facebook_share.png')
        self.assert_snapshot_match(token_path('officer_1_twitter_share.png'), 'officer_1_twitter_share.png')
