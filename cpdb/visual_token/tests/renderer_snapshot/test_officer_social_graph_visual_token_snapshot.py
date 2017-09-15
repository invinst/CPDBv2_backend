from django.conf import settings

from snapshot_test.mixins import SnapshotTestMixin
from mock import patch

from data.factories import OfficerFactory, AllegationFactory, OfficerAllegationFactory
from visual_token.renderers import OfficerSocialGraphVisualTokenRenderer
from .base import RendererSnapshotTestCase


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

    def test_each_background_color(self):
        crs = [0, 3, 7, 20, 30, 45]

        for ind, cr in enumerate(crs):
            id = int('2%d' % ind)
            officer = OfficerFactory(first_name='John', last_name='Doe', id=id)
            with patch('data.models.Officer.allegation_count', cr):
                self.engine.generate_visual_token(officer)
            self.assert_snapshot_match(
                token_path('officer_%d_facebook_share.png' % id), 'officer_%d_facebook_share.png' % id)

    def test_multiple_coaccused(self):
        allegation = AllegationFactory()
        officer1 = OfficerFactory(first_name='Jesse', last_name='Acosta', id=30)
        OfficerAllegationFactory(officer=officer1, allegation=allegation)
        officer2 = OfficerFactory(first_name='Raymond', last_name='Piwnicki', id=31)
        OfficerAllegationFactory(officer=officer2, allegation=allegation)
        officer3 = OfficerFactory(first_name='Jerome', last_name='Finnigan', id=32)
        OfficerAllegationFactory(officer=officer3, allegation=allegation)
        OfficerAllegationFactory.create_batch(7, officer=officer3)

        self.engine.generate_visual_token(officer1)
        self.assert_snapshot_match(token_path('officer_30.svg'), 'officer_30.svg')
