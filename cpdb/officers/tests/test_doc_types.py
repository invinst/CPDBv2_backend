from django.test import SimpleTestCase
from robber import expect

from officers.doc_types import OfficerInfoDocType
from officers.tests.mixins import OfficerSummaryTestCaseMixin

from officers.index_aliases import officers_index_alias


class OfficerInfoDocTypeTestCase(OfficerSummaryTestCaseMixin, SimpleTestCase):
    def tearDown(self):
        officers_index_alias.read_index.delete(ignore=404)

    def test_get_top_officers(self):
        OfficerInfoDocType(
            id='2665',
            full_name='Daryl Smith',
            percentiles=[
                {
                    'percentile_allegation': 99.345,
                    'percentile_trr': 0.000,
                    'year': 2001,
                    'id': 26675,
                    'percentile_allegation_civilian': 98.434,
                    'percentile_allegation_internal': 99.784,
                },
            ]
        ).save()
        OfficerInfoDocType(
            id='2665',
            full_name='Daryl Smith',
            percentiles=[
                {
                    'percentile_allegation': 66.321,
                    'percentile_trr': 0.000,
                    'year': 2001,
                    'id': 26675,
                    'percentile_allegation_civilian': 56.434,
                    'percentile_allegation_internal': 67.784,
                },
            ]
        ).save()
        officers_index_alias.read_index.refresh()

        results = OfficerInfoDocType.get_top_officers()
        expect(results).to.have.length(1)
        expect(results[0].to_dict()).to.eq({
            'id': '2665',
            'full_name': 'Daryl Smith',
            'percentiles': [
                {
                    'percentile_allegation': 99.345,
                    'percentile_trr': 0.000,
                    'year': 2001,
                    'id': 26675,
                    'percentile_allegation_civilian': 98.434,
                    'percentile_allegation_internal': 99.784
                }
            ]
        })
