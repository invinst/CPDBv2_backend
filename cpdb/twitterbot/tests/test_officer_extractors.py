from django.test import TestCase

from robber import expect

from data.factories import OfficerFactory
from twitterbot.officer_extractors import ElasticSearchOfficerExtractor
from twitterbot.tests.mixins import RebuildIndexMixin


class OfficerExtractorTestCase(RebuildIndexMixin, TestCase):
    def check_result_match_officer(self, result, officers):
        expect(result).to.have.length(len(officers))
        expect([obj['id'] for _, obj in result]).to.eq([officer.id for officer in officers])


class ElasticSearchOfficerExtractorTestCase(OfficerExtractorTestCase):
    def setUp(self):
        super(ElasticSearchOfficerExtractorTestCase, self).setUp()
        self.extractor = ElasticSearchOfficerExtractor()

    def test_find_officer(self):
        officer = OfficerFactory(first_name='Michael', last_name='Flynn')

        self.refresh_index()

        self.check_result_match_officer(
            self.extractor.get_officers([('text', 'Michael')]),
            [officer]
        )
        self.check_result_match_officer(
            self.extractor.get_officers([('text', 'Micha')]),
            [officer]
        )
        self.check_result_match_officer(
            self.extractor.get_officers([('text', 'Flynn')]),
            [officer]
        )
        self.check_result_match_officer(
            self.extractor.get_officers([('text', 'Michael Flynn')]),
            [officer]
        )
        self.check_result_match_officer(
            self.extractor.get_officers([('text', 'Flynn Michael')]),
            [officer]
        )

    def test_find_multiple_officers(self):
        officer1 = OfficerFactory(first_name='Michael', last_name='Flynn')
        officer2 = OfficerFactory(first_name='Roman', last_name='Glynn')

        self.refresh_index()

        self.check_result_match_officer(
            self.extractor.get_officers([('text', 'Michael'), ('text', 'Glynn')]),
            [officer1, officer2]
        )

    def test_find_only_officer_with_highest_complaint_count(self):
        OfficerFactory(first_name='Michael', last_name='Flynn', allegation_count=2)
        officer2 = OfficerFactory(first_name='Michael', last_name='Glynn', allegation_count=3)

        self.refresh_index()

        self.check_result_match_officer(
            self.extractor.get_officers([('text', 'Michael')]),
            [officer2]
        )

    def test_find_officer_with_correct_match(self):
        officer = OfficerFactory(first_name='Michael', last_name='Flynn')

        self.refresh_index()

        self.check_result_match_officer(
            self.extractor.get_officers([('text', 'Michael')]),
            [officer]
        )
        self.check_result_match_officer(
            self.extractor.get_officers([('text', 'Michael Glynn')]),
            []
        )
