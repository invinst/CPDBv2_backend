from django.test import TestCase, override_settings

from mock import Mock, patch, mock_open
from robber import expect

from visual_token.engine import Engine, cleanup_child_processes, open_engine


class EngineTestCase(TestCase):
    def setUp(self):
        self.engine = Engine()
        self.engine.driver = Mock()
        self.engine.renderer = Mock(
            blob_name=Mock(return_value='some_blob'),
            serialize=Mock(return_value='some_serialized_data')
        )

    def test_set_renderer(self):
        renderer = Mock()
        self.engine.set_renderer(renderer)
        expect(self.engine.renderer).to.eq(renderer)

    @override_settings(RUNNING_PORT='1080')
    def test_server_base_path(self):
        expect(self.engine.server_base_path).to.eq('http://localhost:1080')

    def generate_visual_token(self):
        self.engine.driver.execute_script.return_value = ['some_color', 'some_svg_str']
        self.engine.generate_visual_token('some_data')
        self.engine.save_svg = Mock()
        self.engine.snap_facebook_picture = Mock()
        self.engine.snap_twitter_picture = Mock()

        expect(self.engine.renderer).to.be.called_once_with('some_data')
        expect(self.engine.driver.execute_script).to.be.called_once_with('''
            var data = arguments[0];
            return window.render(data);
            ''', 'some_serialized_data')
        expect(self.engine.save_svg).to.be.called_once_with('some_data', 'some_svg_str')
        expect(self.engine.snap_facebook_picture).to.be.called_once_with('some_data')
        expect(self.engine.snap_twitter_picture).to.be.called_once_with('some_data')

    @override_settings(VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER='somefolder')
    def test_save_svg(self):
        _mock_open = mock_open()
        with patch('visual_token.engine.open', _mock_open, create=True):
            self.engine.save_svg('some_data', 'some_svg_string')

            expect(_mock_open).to.be.called_once_with('somefolder/some_blob.svg', 'w')
            expect(_mock_open().write).to.be.called_once_with('some_svg_string')

    @override_settings(VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER='somefolder')
    def test_snap_facebook_picture(self):
        self.engine.snap_facebook_picture('some_data')

        expect(self.engine.renderer.blob_name).to.be.called_once_with('some_data')
        expect(self.engine.driver.set_window_size).to.be.called_once_with(width=1200, height=627)
        expect(self.engine.driver.get_screenshot_as_file).to.be.called_once_with(
            'somefolder/some_blob_facebook_share.png'
        )

    @override_settings(VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER='somefolder')
    def test_twitter_picture(self):
        self.engine.snap_twitter_picture('some_data')

        expect(self.engine.renderer.blob_name).to.be.called_once_with('some_data')
        expect(self.engine.driver.set_window_size).to.be.called_once_with(width=1200, height=600)
        expect(self.engine.driver.get_screenshot_as_file).to.be.called_once_with(
            'somefolder/some_blob_twitter_share.png'
        )

    def test_close_all_windows(self):
        self.engine.close_all_windows()
        expect(self.engine.driver.quit).to.be.called_once()

    @patch('visual_token.engine.engine')
    def test_open_engine(self, _):
        renderer = Mock()
        with open_engine(renderer) as engine:
            expect(engine.set_renderer).to.be.called_once_with(renderer)
            expect(engine.start).to.be.called_once()
        expect(engine.close_all_windows).to.be.called_once()

    @patch('visual_token.engine.engine.close_all_windows')
    @patch('visual_token.engine.service.stop', side_effect=AttributeError)
    def test_cleanup_child_processes(self, mock_stop, mock_close_all_windows):
        cleanup_child_processes()
        expect(mock_close_all_windows).to.be.called_once()
        expect(mock_stop).to.be.called_once()
