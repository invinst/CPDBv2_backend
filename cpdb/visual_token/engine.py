import atexit
from contextlib import contextmanager

from django.conf import settings
from django.urls import reverse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


service = webdriver.chrome.service.Service("chromedriver")


class Engine:
    def set_renderer(self, renderer):
        self.renderer = renderer

    @property
    def server_base_path(self):
        return 'http://localhost:%s' % settings.RUNNING_PORT

    def start(self):
        try:
            service_url = settings.SELENIUM_URL
        except AttributeError:
            service.start()
            service_url = service.service_url

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        capabilities = chrome_options.to_capabilities()

        self.driver = webdriver.Remote(service_url, desired_capabilities=capabilities)
        self.driver.get(
            '%s%s' % (
                self.server_base_path, reverse('visual_token', args=[self.renderer.script_path])))

        self.driver.execute_async_script('''
            var done = arguments[0];
            var interval = setInterval(function () {
                if (window.render && window.d3) {
                    clearInterval(interval);
                    done();
                }
            }, 500);''')

    def generate_visual_token(self, data):
        svg_str = self.driver.execute_script('''
            var data = arguments[0];
            return window.render(data);
            ''', self.renderer.serialize(data))

        self.save_svg(data, svg_str)
        self.snap_png(data)

    def save_svg(self, data, svg_str):
        filename = '%s/%s.svg' % (settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER, self.renderer.blob_name(data))
        with open(filename, 'w') as file:
            file.write(svg_str)

    def snap_png(self, data):
        self.driver.set_window_size(width=1200, height=627)
        self.driver.get_screenshot_as_file(
            '%s/%s.png' % (settings.VISUAL_TOKEN_SOCIAL_MEDIA_FOLDER, self.renderer.blob_name(data)))

    def close_all_windows(self):
        if hasattr(self, 'driver'):
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
    try:
        service.stop()
    except AttributeError:
        pass
