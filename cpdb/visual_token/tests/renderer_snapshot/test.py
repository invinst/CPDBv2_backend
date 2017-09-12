import os

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from mock import Mock

from visual_token.engine import engine


class RendererSnapshotTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(RendererSnapshotTestCase, cls).setUpClass()
        if not os.path.isdir(settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER):
            os.makedirs(settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER)
        cls.renderer = cls.renderer_class()
        cls.engine = engine
        cls.engine.server_base_path = Mock(return_value=cls.live_server_url)
        cls.engine.set_renderer(cls.renderer)
        cls.engine.start()

    @classmethod
    def tearDownClass(cls):
        super(RendererSnapshotTestCase, cls).tearDownClass()
        cls.engine.close_all_windows()
