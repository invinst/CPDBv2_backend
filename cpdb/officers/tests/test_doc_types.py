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
            id='1',
            full_name='Daryl Smith',
            has_visual_token=True,
            current_allegation_percentile=99.345,
        ).save()
        OfficerInfoDocType(
            id='2',
            full_name='Officer highest percentile',
            has_visual_token=True,
            current_allegation_percentile=99.5,
        ).save()
        OfficerInfoDocType(
            id='3',
            full_name='Officer low percentile',
            has_visual_token=True,
            current_allegation_percentile=96.345,
        ).save()
        OfficerInfoDocType(
            id='4',
            full_name='Officer no visual token',
            has_visual_token=False,
            current_allegation_percentile=99.88,
        ).save()
        OfficerInfoDocType(
            id='5',
            full_name='Officer filter out',
            has_visual_token=True,
            current_allegation_percentile=99.2,
        ).save()
        OfficerInfoDocType(
            id='6',
            full_name='Officer no allegation_percentile',
            has_visual_token=True,
            current_allegation_percentile=None,
        ).save()
        officers_index_alias.read_index.refresh()

        results = OfficerInfoDocType.get_top_officers(size=2)
        expect(results).to.have.length(2)
        expect(results[0].id).to.eq('2')
        expect(results[1].id).to.eq('1')
