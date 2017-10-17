from django.test import SimpleTestCase

from mock import patch
from robber import expect

from visual_token.utils import clear_folder


class ClearFolderTestCase(SimpleTestCase):
    @patch('visual_token.utils.shutil.rmtree', side_effect=OSError)
    @patch('visual_token.utils.os.makedirs')
    def test_clear_folder(self, makedirs, rmtree):
        clear_folder('abc')
        expect(rmtree).to.be.called_with('abc')
        expect(makedirs).to.be.called_with('abc')
