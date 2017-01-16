from mock import Mock, patch

from django.test import TestCase

from robber import expect

from ..utils import get_faq_parent_node


class UtilsTestCase(TestCase):
    @patch('faq.utils.FAQPage.get_root_nodes')
    def test_get_faq_parent_node(self, get_root_nodes):
        root_node = Mock(get_first_child=Mock(return_value='something'))
        get_root_nodes.return_value = [root_node]

        expect(get_faq_parent_node()).to.be.equal('something')
