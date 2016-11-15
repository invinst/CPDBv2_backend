from django.test import SimpleTestCase

from cms.factories import LinkEntityFactory


class LinkEntityFactoryTestCase(SimpleTestCase):
    def test_factory(self):
        link_entity = LinkEntityFactory(url='url')
        self.assertEqual(link_entity.data['url'], 'url')
