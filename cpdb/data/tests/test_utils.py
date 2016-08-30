from django.test import TestCase

from data.utils import get_model
from story.models import Story


class UtilsTestCase(TestCase):
    def test_get_model(self):
        self.assertEqual(get_model('story.Story'), Story)
