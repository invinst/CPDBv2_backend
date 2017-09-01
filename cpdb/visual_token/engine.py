import os
import atexit
from contextlib import contextmanager

from django.conf import settings

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from visual_token.utils import execute_visual_token_script


service = webdriver.chrome.service.Service(os.path.abspath("chromedriver"))


class Engine:
    def set_renderer(self, renderer):
        self.renderer = renderer

    def start(self):
        service.start()

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        self.driver = webdriver.Remote(service.service_url, desired_capabilities=chrome_options.to_capabilities())
        self.driver.get('about:blank')

        execute_visual_token_script(self.driver, 'js/inject_css.js')
        execute_visual_token_script(self.driver, 'js/inject_d3.js')
        execute_visual_token_script(self.driver, 'js/engine.js')
        execute_visual_token_script(self.driver, self.renderer.script_path)

    def generate_visual_token(self, data):
        execute_visual_token_script(self.driver, 'js/render.js', self.renderer.serialize(data))
        self.snap_facebook_picture(data)
        self.snap_twitter_picture(data)

    def snap_facebook_picture(self, data):
        self.driver.set_window_rect(0, 0, 1200, 627)
        self.driver.get_screenshot_as_file(
            '%s/%s' % (settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER, self.renderer.facebook_share_filename(data)))

    def snap_twitter_picture(self, data):
        self.driver.set_window_rect(0, 15, 1200, 600)
        self.driver.get_screenshot_as_file(
            '%s/%s' % (settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER, self.renderer.twitter_share_filename(data)))

    def close_all_windows(self):
        self.driver.quit()


engine = Engine()


@contextmanager
def open_engine(renderer):
    engine.set_renderer(renderer)
    engine.start()
    yield engine
    engine.close_all_windows()


@atexit.register
def cleanup_child_processes():
    engine.close_all_windows()
    service.stop()
