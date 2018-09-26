from datetime import date, datetime

import pytz
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from robber import expect
from mock import patch

from data.tests.officer_percentile_utils import mock_percentile_map_range
from officers.tests.mixins import OfficerSummaryTestCaseMixin
from data.constants import ACTIVE_YES_CHOICE
from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, PoliceUnitFactory,
    AllegationCategoryFactory, OfficerHistoryFactory, OfficerBadgeNumberFactory, AwardFactory, ComplainantFactory,
    SalaryFactory,
    AttachmentFileFactory,
)
from trr.factories import TRRFactory


class OfficersMobileViewSetTestCase(OfficerSummaryTestCaseMixin, APITestCase):

    @patch('officers.indexers.officers_indexer.MIN_VISUAL_TOKEN_YEAR', 2002)
    @patch('officers.indexers.officers_indexer.MAX_VISUAL_TOKEN_YEAR', 2002)
    def test_retrieve_data_range_too_small_cause_no_percentiles(self):

        officer = OfficerFactory(
            tags=[],
            first_name='Kevin', last_name='Kerl', id=123, race='White', gender='M',
            appointed_date=date(2002, 2, 27), rank='PO', resignation_date=date(2017, 12, 27),
            active=ACTIVE_YES_CHOICE, birth_year=1960, complaint_percentile=32.5
        )
        allegation = AllegationFactory(incident_date=datetime(2002, 3, 1, tzinfo=pytz.utc))
        internal_allegation = AllegationFactory(
            incident_date=datetime(2002, 4, 1, tzinfo=pytz.utc),
            is_officer_complaint=True
        )
        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerHistoryFactory(
            officer=officer, effective_date=datetime(2002, 2, 27, tzinfo=pytz.utc),
            unit=PoliceUnitFactory(id=1, unit_name='CAND', description='')
        )
        ComplainantFactory(allegation=allegation, race='White', age=18, gender='F')
        OfficerBadgeNumberFactory(officer=officer, star='123456', current=True)
        OfficerBadgeNumberFactory(officer=officer, star='789', current=False)
        OfficerAllegationFactory(
            officer=officer, allegation=allegation, allegation_category=allegation_category,
            final_finding='SU', start_date=date(2002, 3, 2), disciplined=True
        )
        OfficerAllegationFactory(
            officer=officer, allegation=internal_allegation,
            final_finding='NS', start_date=date(2002, 3, 2), disciplined=False
        )
        AwardFactory(officer=officer, award_type='Complimentary Letter', start_date=date(2014, 5, 1))
        AwardFactory(officer=officer, award_type='Honored Police Star', start_date=date(2014, 6, 1))
        AwardFactory(officer=officer, award_type='Honorable Mention', start_date=date(2014, 7, 1))
        SalaryFactory(officer=officer, salary=50000, year=2002)
        SalaryFactory(officer=officer, salary=90000, year=2017)
        TRRFactory(officer=officer, trr_datetime=datetime(2002, 3, 1, tzinfo=pytz.utc))

        second_officer = OfficerFactory(
            tags=[],
            first_name='Kevin', last_name='Osborn', id=456, race='Black', gender='M',
            appointed_date=date(2002, 1, 27), resignation_date=date(2017, 12, 27), rank='PO',
            active=ACTIVE_YES_CHOICE, birth_year=1970
        )
        TRRFactory(officer=second_officer, trr_datetime=datetime(2002, 5, 1, tzinfo=pytz.utc))
        TRRFactory(officer=second_officer, trr_datetime=datetime(2002, 12, 1, tzinfo=pytz.utc))

        OfficerFactory(
            tags=[],
            first_name='Kevin', last_name='Edward', id=789, race='Black', gender='M',
            appointed_date=date(2002, 3, 27), resignation_date=date(2017, 12, 27), rank='PO',
            active=ACTIVE_YES_CHOICE, birth_year=1970
        )

        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-mobile-detail', kwargs={'pk': 123}))
        expected_response = {
            'officer_id': 123,
            'unit': {
                'unit_id': 1,
                'unit_name': 'CAND',
                'description': '',
            },
            'date_of_appt': '2002-02-27',
            'date_of_resignation': '2017-12-27',
            'active': True,
            'rank': 'PO',
            'full_name': 'Kevin Kerl',
            'race': 'White',
            'badge': '123456',
            'historic_badges': ['789'],
            'gender': 'Male',
            'birth_year': 1960,
            'sustained_count': 1,
            'civilian_compliment_count': 1,
            'allegation_count': 2,
            'discipline_count': 1,
            'honorable_mention_count': 1,
            'trr_count': 1,
            'major_award_count': 1,
            'complaint_percentile': 32.5,
        }
        expect(response.data).to.eq(expected_response)

    @patch('officers.indexers.officers_indexer.MIN_VISUAL_TOKEN_YEAR', 2002)
    @patch('officers.indexers.officers_indexer.MAX_VISUAL_TOKEN_YEAR', 2004)
    @mock_percentile_map_range(
        allegation_min=datetime(2002, 1, 1, tzinfo=pytz.utc),
        allegation_max=datetime(2044, 12, 31, tzinfo=pytz.utc),
        internal_civilian_min=datetime(2002, 1, 1, tzinfo=pytz.utc),
        internal_civilian_max=datetime(2004, 12, 31, tzinfo=pytz.utc),
        trr_min=datetime(2002, 3, 1, tzinfo=pytz.utc),
        trr_max=datetime(2004, 12, 31, tzinfo=pytz.utc)
    )
    def test_retrieve(self):

        # main officer
        officer = OfficerFactory(
            tags=[],
            first_name='Kevin', last_name='Kerl', id=123, race='White', gender='M',
            appointed_date=date(2002, 2, 27), rank='PO', resignation_date=date(2017, 12, 27),
            active=ACTIVE_YES_CHOICE, birth_year=1960, complaint_percentile=32.5,
            honorable_mention_percentile=66.6667
        )

        allegation = AllegationFactory(incident_date=datetime(2002, 3, 1, tzinfo=pytz.utc))
        internal_allegation_2003 = AllegationFactory(
            incident_date=datetime(2003, 4, 1, tzinfo=pytz.utc),
            is_officer_complaint=True
        )
        internal_allegation_2004 = AllegationFactory(
            incident_date=datetime(2004, 7, 1, tzinfo=pytz.utc),
            is_officer_complaint=True
        )

        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerAllegationFactory(
            officer=officer, allegation=allegation, allegation_category=allegation_category,
            final_finding='SU', start_date=date(2002, 3, 2), disciplined=True
        )
        OfficerAllegationFactory(
            officer=officer, allegation=internal_allegation_2003,
            final_finding='NS', start_date=date(2003, 5, 2), disciplined=False
        )
        OfficerAllegationFactory(
            officer=officer, allegation=internal_allegation_2004,
            final_finding='NS', start_date=date(2004, 8, 2), disciplined=False
        )

        ComplainantFactory(allegation=allegation, race='White', age=18, gender='F')

        OfficerHistoryFactory(
            officer=officer, effective_date=datetime(2002, 2, 27, tzinfo=pytz.utc),
            unit=PoliceUnitFactory(id=1, unit_name='CAND', description='')
        )
        OfficerBadgeNumberFactory(officer=officer, star='123456', current=True)
        OfficerBadgeNumberFactory(officer=officer, star='789', current=False)
        AwardFactory(officer=officer, award_type='Complimentary Letter', start_date=date(2012, 5, 1))
        AwardFactory(officer=officer, award_type='Honored Police Star', start_date=date(2013, 6, 1))
        AwardFactory(officer=officer, award_type='Honorable Mention', start_date=date(2014, 7, 1))
        SalaryFactory(officer=officer, salary=50000, year=2002)
        SalaryFactory(officer=officer, salary=90000, year=2017)
        TRRFactory(officer=officer, trr_datetime=datetime(2002, 3, 1, tzinfo=pytz.utc))

        # second officer
        second_officer = OfficerFactory(
            tags=[],
            first_name='Kevin', last_name='Osborn', id=456, race='Black', gender='M',
            appointed_date=date(2002, 1, 27), rank='PO',
            active=ACTIVE_YES_CHOICE, birth_year=1970
        )
        TRRFactory(officer=second_officer, trr_datetime=datetime(2003, 5, 1, tzinfo=pytz.utc))
        TRRFactory(officer=second_officer, trr_datetime=datetime(2004, 12, 1, tzinfo=pytz.utc))

        # third officer
        OfficerFactory(
            tags=[],
            first_name='Kevin', last_name='Edward', id=789, race='Black', gender='M',
            appointed_date=date(2003, 3, 27), rank='PO',
            active=ACTIVE_YES_CHOICE, birth_year=1970
        )

        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-mobile-detail', kwargs={'pk': 123}))
        expected_response = {
            'officer_id': 123,
            'unit': {
                'unit_id': 1,
                'unit_name': 'CAND',
                'description': '',
            },
            'percentiles': [
                {
                    'id': 123,
                    'year': 2003,
                    'percentile_trr': u'0.0000',
                    'percentile_allegation': u'50.0000',
                    'percentile_allegation_civilian': u'50.0000',
                    'percentile_allegation_internal': u'50.0000'
                },
                {
                    'id': 123,
                    'year': 2004,
                    'percentile_trr': u'33.3333',
                    'percentile_allegation': u'66.6667',
                    'percentile_allegation_civilian': u'66.6667',
                    'percentile_allegation_internal': u'66.6667'
                },
            ],
            'date_of_appt': '2002-02-27',
            'date_of_resignation': '2017-12-27',
            'active': True,
            'rank': 'PO',
            'full_name': 'Kevin Kerl',
            'race': 'White',
            'badge': '123456',
            'historic_badges': ['789'],
            'gender': 'Male',
            'birth_year': 1960,
            'sustained_count': 1,
            'civilian_compliment_count': 1,
            'allegation_count': 3,
            'discipline_count': 1,
            'honorable_mention_count': 1,
            'trr_count': 1,
            'major_award_count': 1,
            'complaint_percentile': 32.5,
            'honorable_mention_percentile': 66.6667,
        }
        expect(response.data).to.eq(expected_response)

    def test_retrieve_no_match(self):
        self.refresh_index()
        response = self.client.get(reverse('api-v2:officers-mobile-detail', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_new_timeline_items_no_match(self):
        response = self.client.get(reverse('api-v2:officers-mobile-new-timeline-items', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_new_timeline_item(self):
        officer = OfficerFactory(id=123, appointed_date=date(2000, 1, 1), rank='Police Officer')

        unit1 = PoliceUnitFactory(unit_name='001', description='unit_001')
        unit2 = PoliceUnitFactory(unit_name='002', description='unit_002')
        OfficerHistoryFactory(officer=officer, unit=unit1, effective_date=date(2010, 1, 1), end_date=date(2011, 12, 31))
        OfficerHistoryFactory(officer=officer, unit=unit2, effective_date=date(2012, 1, 1), end_date=None)

        AwardFactory(officer=officer, start_date=date(2011, 3, 23), award_type='Honorable Mention')
        AwardFactory(officer=officer, start_date=date(2015, 3, 23), award_type='Complimentary Letter')
        AwardFactory(officer=officer, start_date=date(2011, 3, 23), award_type='Life Saving Award')
        allegation = AllegationFactory(crid='123456')
        AttachmentFileFactory(
            allegation=allegation,
            title='CRID-303350-CR',
            file_type='document',
            url='https://www.documentcloud.org/documents/3518955-CRID-303350-CR.pdf'
        )
        OfficerAllegationFactory(
            final_finding='UN', final_outcome='Unknown',
            officer=officer, start_date=date(2011, 8, 23), allegation=allegation,
            allegation_category=AllegationCategoryFactory(category='category', allegation_name='sub category')
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)

        allegation2 = AllegationFactory(crid='654321')
        OfficerAllegationFactory(
            final_finding='UN', final_outcome='9 Day Suspension',
            officer=officer, start_date=date(2015, 8, 23), allegation=allegation2,
            allegation_category=AllegationCategoryFactory(category='Use of Force', allegation_name='sub category')
        )

        trr2011 = TRRFactory(officer=officer, trr_datetime=datetime(2011, 9, 23), taser=True, firearm_used=False)
        trr2015 = TRRFactory(officer=officer, trr_datetime=datetime(2015, 9, 23), taser=False, firearm_used=False)
        SalaryFactory(officer=officer, rank='Police Officer', spp_date=date(1998, 9, 23))

        self.refresh_index()
        response = self.client.get(reverse('api-v2:officers-mobile-new-timeline-items', kwargs={'pk': 123}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'trr_id': trr2015.id,
                'date': '2015-09-23',
                'kind': 'FORCE',
                'taser': False,
                'firearm_used': False,
                'unit_name': '002',
                'unit_description': 'unit_002',
                'rank': 'Police Officer',
            }, {
                'date': '2015-08-23',
                'kind': 'CR',
                'crid': '654321',
                'category': 'Use of Force',
                'subcategory': 'sub category',
                'finding': 'Unfounded',
                'outcome': '9 Day Suspension',
                'coaccused': 1,
                'unit_name': '002',
                'unit_description': 'unit_002',
                'rank': 'Police Officer',
            }, {
                'date': '2012-01-01',
                'kind': 'UNIT_CHANGE',
                'unit_name': '002',
                'unit_description': 'unit_002',
                'rank': 'Police Officer',
            }, {
                'trr_id': trr2011.id,
                'date': '2011-09-23',
                'kind': 'FORCE',
                'taser': True,
                'firearm_used': False,
                'unit_name': '001',
                'unit_description': 'unit_001',
                'rank': 'Police Officer',
            }, {
                'date': '2011-08-23',
                'kind': 'CR',
                'crid': '123456',
                'category': 'category',
                'subcategory': 'sub category',
                'finding': 'Unfounded',
                'outcome': 'Unknown',
                'coaccused': 4,
                'unit_name': '001',
                'unit_description': 'unit_001',
                'rank': 'Police Officer',
                'attachments': [{
                    'file_type': 'document',
                    'url': 'https://www.documentcloud.org/documents/3518955-CRID-303350-CR.pdf',
                    'preview_image_url': None,
                    'title': 'CRID-303350-CR'
                }]
            }, {
                'date': '2011-03-23',
                'kind': 'AWARD',
                'award_type': 'Life Saving Award',
                'unit_name': '001',
                'unit_description': 'unit_001',
                'rank': 'Police Officer',
            }, {
                'date': '2010-01-01',
                'kind': 'UNIT_CHANGE',
                'unit_name': '001',
                'unit_description': 'unit_001',
                'rank': 'Police Officer',
            }, {
                'date': '2000-01-01',
                'kind': 'JOINED',
                'unit_name': '',
                'unit_description': '',
                'rank': 'Police Officer',
            },
        ])
