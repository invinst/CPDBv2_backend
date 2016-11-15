from django.test import SimpleTestCase

from mock import patch

from cms.utils import generate_draft_block_key


class UtilsTestCase(SimpleTestCase):
    def test_generate_draft_block_key(self):
        with patch('cms.utils.uuid.uuid4', return_value='a1234'):
            self.assertEqual(generate_draft_block_key(), 'a1234')
