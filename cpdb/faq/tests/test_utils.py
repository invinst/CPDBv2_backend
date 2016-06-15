from django.test.testcases import TestCase
from django.contrib.contenttypes.models import ContentType

from wagtail.wagtailcore.models import Page

from faq.models import FAQPage
from faq.utils import get_faq_parent_node


class UtilsTestCase(TestCase):
    def setUp(self):
        FAQPage.get_tree().all().delete()

    def test_get_faq_parent_node(self):
        content_type = ContentType.objects.get_for_model(Page)

        root = FAQPage.add_root(
            instance=Page(title='Root', slug='root', content_type=content_type))

        expected_home_node = root.add_child(instance=Page(title='Home', slug='home', content_type=content_type))

        home_node = get_faq_parent_node()

        self.assertEqual(home_node, expected_home_node)
