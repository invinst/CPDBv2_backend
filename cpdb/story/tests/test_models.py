from django.test.testcases import SimpleTestCase

from story.models import Newspaper


class NewsPaperModelTestCase(SimpleTestCase):
    def test_unicode_display(self):
        paper_name = 'a'
        newspaper = Newspaper(name=paper_name)
        self.assertIn(paper_name, repr(newspaper))
