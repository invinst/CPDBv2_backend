from pandas import DataFrame
from robber import expect

from django.test import SimpleTestCase

from data_importer.base.linkable_searcher import LinkableSearcher, PoliceUnitLinkableSearcher


class LinkableSearcherTestCase(SimpleTestCase):
    def test_search_by_same_name(self):
        officer1 = {'first_name': 'Foo', 'last_name': 'Bar', 'gender': 'F'}
        officer2 = {'first_name': 'Foo', 'last_name': 'Baz', 'gender': 'M'}
        df_officers = DataFrame.from_dict([officer1, officer2])

        linkable_searcher = LinkableSearcher(df_officers, 'SAME_NAME')
        result = linkable_searcher.search({'first_name': 'Foo', 'last_name': 'Bar'})
        expect(len(result)).to.be.eq(1)
        expect(dict(result.iloc[0])).to.be.eq(officer1)

    def test_search_by_marriage(self):
        officer1 = {'first_name': 'Foo', 'last_name': 'Bar', 'gender': 'F'}
        officer2 = {'first_name': 'Foo', 'last_name': 'Baz', 'gender': 'M'}
        df_officers = DataFrame.from_dict([officer1, officer2])

        linkable_searcher = LinkableSearcher(df_officers, 'MARRIAGE')
        result = linkable_searcher.search({'first_name': 'Foo'})
        expect(len(result)).to.be.eq(1)
        expect(dict(result.iloc[0])).to.be.eq(officer1)


class PoliceUnitLinkableSearcherTestCase(SimpleTestCase):
    def test_search(self):
        unit1 = {'unit_name': '001', 'description': 'description1'}
        unit2 = {'unit_name': '002', 'description': 'description1'}
        df_units = DataFrame.from_dict([unit1, unit2])

        police_unit_linkable_searcher = PoliceUnitLinkableSearcher(df_units, profile_prefix='')
        expect(police_unit_linkable_searcher.search({'unit_name': '001'})).to.have.length(1)
        expect(police_unit_linkable_searcher.search({'unit_name': '003'})).to.have.length(0)
