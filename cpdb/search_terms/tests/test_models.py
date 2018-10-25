from django.test import TestCase

from robber import expect

from search_terms.models import SearchTermCategory, SearchTermItem


class SearchTermCategoryTestCase(TestCase):
    def test_unicode(self):
        search_term = SearchTermCategory(name='Geography')
        expect(str(search_term)).to.eq('Geography')


class SearchTermItemTestCase(TestCase):
    def test_unicode(self):
        search_term = SearchTermItem(name='Police District')
        expect(str(search_term)).to.eq('Police District')

    def test_v1_url(self):
        search_term = SearchTermItem(link='/url-mediator/session-builder?community=abc')
        expect(search_term.v1_url).to.eq('http://cpdb.lvh.me/url-mediator/session-builder?community=abc')
