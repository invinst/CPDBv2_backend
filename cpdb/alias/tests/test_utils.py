from robber import expect
from django.test import TestCase

from search.tests.utils import IndexMixin
from data.factories import OfficerFactory
from search.search_indexers import OfficerIndexer
from data.models import Officer
from search.doc_types import OfficerDocType
from cpdb.alias.utils import set_aliases


class AliasUtilsTestCase(IndexMixin, TestCase):
    allow_database_queries = True

    def setUp(self):
        super(AliasUtilsTestCase, self).setUp()
        self.officer = OfficerFactory(id=1)
        self.officer_doc = OfficerDocType(meta={'id': '1'})
        self.officer_doc.save()
        self.refresh_index()

    def test_set_officer_aliases(self):
        set_aliases(OfficerIndexer, '1', ['alias1', 'alias2'])
        expect(OfficerDocType.get('1').tags).to.eq(['alias1', 'alias2'])
        expect(Officer.objects.get(pk=1).tags).to.eq(['alias1', 'alias2'])
