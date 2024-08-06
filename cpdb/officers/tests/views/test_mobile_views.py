from datetime import date, datetime

from django.urls import reverse
from django.contrib.gis.geos import Point
from rest_framework import status
from rest_framework.test import APITestCase

import pytz
from robber import expect
from mock import patch

from lawsuit.factories import LawsuitFactory, PaymentFactory
from data.tests.officer_percentile_utils import mock_percentile_map_range
from officers.tests.mixins import OfficerSummaryTestCaseMixin
from data.constants import ACTIVE_YES_CHOICE
from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, PoliceUnitFactory,
    AllegationCategoryFactory, OfficerHistoryFactory, OfficerBadgeNumberFactory, AwardFactory,
    ComplainantFactory, SalaryFactory, VictimFactory, OfficerAliasFactory
)
from trr.factories import TRRFactory
from data import cache_managers
from data.cache_managers import officer_cache_manager, allegation_cache_manager
from lawsuit.cache_managers import lawsuit_cache_manager
from data.models import OfficerYearlyPercentile


class OfficersMobileViewSetTestCase(OfficerSummaryTestCaseMixin, APITestCase):

    @patch('officers.indexers.officers_indexer.MIN_VISUAL_TOKEN_YEAR', 2002)
    @patch('officers.indexers.officers_indexer.MAX_VISUAL_TOKEN_YEAR', 2002)
    def test_retrieve_data_range_too_small_cause_no_percentiles(self):

        officer = OfficerFactory(
            tags=[],
            first_name='Kevin', last_name='Kerl', id=123, race='White', gender='M',
            appointed_date=date(2002, 2, 27), rank='PO', resignation_date=date(2017, 12, 27),
            active=ACTIVE_YES_CHOICE, birth_year=1960, complaint_percentile=32.5,
            sustained_count=1, allegation_count=2, discipline_count=1, trr_count=1,
            honorable_mention_count=1, major_award_count=1,
            last_unit_id=1, current_badge='123456'
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

        officer_cache_manager.build_cached_columns()
        allegation_cache_manager.cache_data()

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
            'active': 'Active',
            'rank': 'PO',
            'full_name': 'Kevin Kerl',
            'race': 'White',
            'badge': '123456',
            'historic_badges': ['789'],
            'gender': 'Male',
            'birth_year': 1960,
            'sustained_count': 1,
            'unsustained_count': 1,
            'allegation_count': 2,
            'discipline_count': 1,
            'honorable_mention_count': 1,
            'trr_count': 1,
            'major_award_count': 1,
            'percentile_allegation': '32.5000',
            'percentiles': []
        }
        expect(response.data).to.eq(expected_response)

    @patch('data.cache_managers.officer_cache_manager.MIN_VISUAL_TOKEN_YEAR', 2002)
    @patch('data.cache_managers.officer_cache_manager.MAX_VISUAL_TOKEN_YEAR', 2004)
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
            honorable_mention_percentile=66.6667,
            sustained_count=1, allegation_count=3, discipline_count=1, trr_count=1,
            honorable_mention_count=1, major_award_count=1,
            last_unit_id=1, current_badge='123456'
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

        lawsuit_1 = LawsuitFactory()
        PaymentFactory(settlement=5000, legal_fees=2000, lawsuit=lawsuit_1)
        PaymentFactory(settlement=0, legal_fees=5000, lawsuit=lawsuit_1)
        lawsuit_1.officers.set([officer])
        lawsuit_2 = LawsuitFactory()
        PaymentFactory(settlement=8500, legal_fees=0, lawsuit=lawsuit_2)
        lawsuit_2.officers.set([officer])

        officer_cache_manager.build_cached_yearly_percentiles()
        officer_cache_manager.build_cached_columns()
        allegation_cache_manager.cache_data()
        lawsuit_cache_manager.cache_data()

        yearly_percentiles = OfficerYearlyPercentile.objects.filter(officer_id=123).order_by('year')

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
                    'id': yearly_percentiles[0].id,
                    'year': 2003,
                    'percentile_trr': '0.0000',
                    'percentile_allegation': '50.0000',
                    'percentile_allegation_civilian': '50.0000',
                    'percentile_allegation_internal': '50.0000'
                },
                {
                    'id': yearly_percentiles[1].id,
                    'year': 2004,
                    'percentile_trr': '33.3333',
                    'percentile_allegation': '66.6667',
                    'percentile_allegation_civilian': '66.6667',
                    'percentile_allegation_internal': '66.6667'
                },
            ],
            'date_of_appt': '2002-02-27',
            'date_of_resignation': '2017-12-27',
            'active': 'Active',
            'rank': 'PO',
            'full_name': 'Kevin Kerl',
            'race': 'White',
            'badge': '123456',
            'historic_badges': ['789'],
            'gender': 'Male',
            'birth_year': 1960,
            'sustained_count': 1,
            'unsustained_count': 2,
            'total_lawsuit_settlements': '20500.00',
            'allegation_count': 3,
            'discipline_count': 1,
            'honorable_mention_count': 1,
            'trr_count': 1,
            'major_award_count': 1,
            'percentile_allegation': '32.5000',
            'honorable_mention_percentile': '66.6667',
        }
        expect(response.data).to.eq(expected_response)

    def test_retrieve_no_match(self):
        response = self.client.get(reverse('api-v2:officers-mobile-detail', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_retrieve_with_alias(self):
        officer = OfficerFactory(id=456)
        OfficerAliasFactory(old_officer_id=123, new_officer=officer)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-mobile-detail', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['officer_id']).to.eq(456)

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
        allegation = AllegationFactory(
            crid='123456',
            coaccused_count=4,
            incident_date=datetime(2011, 8, 23, tzinfo=pytz.utc)
        )
        VictimFactory(allegation=allegation, gender='M', race='White', age=34)
        OfficerAllegationFactory(
            final_finding='UN', final_outcome='Unknown',
            officer=officer, allegation=allegation,
            allegation_category=AllegationCategoryFactory(category='category', allegation_name='sub category')
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)

        allegation2 = AllegationFactory(
            crid='654321',
            point=Point(35.5, 68.9),
            coaccused_count=1,
            incident_date=datetime(2015, 8, 23, tzinfo=pytz.utc)
        )
        OfficerAllegationFactory(
            final_finding='UN', final_outcome='9 Day Suspension',
            officer=officer, allegation=allegation2,
            allegation_category=AllegationCategoryFactory(category='Use of Force', allegation_name='sub category')
        )

        trr2011 = TRRFactory(
            officer=officer,
            trr_datetime=datetime(2011, 9, 23, tzinfo=pytz.utc),
            taser=True,
            firearm_used=False
        )
        trr2015 = TRRFactory(
            officer=officer,
            trr_datetime=datetime(2015, 9, 23, tzinfo=pytz.utc),
            taser=False,
            firearm_used=False
        )
        SalaryFactory(officer=officer, year=2001, rank='Police Officer', spp_date=date(2001, 9, 23))
        SalaryFactory(officer=officer, year=2000, rank='Junior Police Officer', spp_date=date(2000, 1, 1))

        cache_managers.cache_all()

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
                'point': {
                    'lon': 35.5,
                    'lat': 68.9
                },
                'victims': [],
                'attachments': []
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
                'victims': [
                    {
                        'race': 'White',
                        'age': 34,
                        'gender': 'Male',
                    }
                ],
                'attachments': [],
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
                'date': '2001-09-23',
                'kind': 'RANK_CHANGE',
                'unit_name': '',
                'unit_description': '',
                'rank': 'Police Officer',
            }, {
                'date': '2000-01-01',
                'kind': 'JOINED',
                'unit_name': '',
                'unit_description': '',
                'rank': 'Junior Police Officer',
            },
        ])

    def test_list_all_invalid_ids(self):
        response = self.client.get(reverse('api-v2:officers-mobile-list'), {'ids': '1,2.0,3'})
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data).to.have.eq('Invalid officer ids: 2.0, 1, 3')

    def test_list(self):
        OfficerFactory(
            id=1, first_name='Daryl', last_name='Mack',
            trr_percentile=12.0000,
            allegation_count=12,
            sustained_count=0,
            civilian_allegation_percentile=99.7840,
            internal_allegation_percentile=99.7840,
            complaint_percentile=99.3450,
            race='White', gender='M', birth_year=1975,
        )
        OfficerFactory(
            id=2,
            first_name='Ronald', last_name='Watts',
            trr_percentile=0.0000,
            allegation_count=5,
            sustained_count=None,
            civilian_allegation_percentile=98.4344,
            internal_allegation_percentile=None,
            complaint_percentile=99.5000,
            race='Black', gender='F', birth_year=1971,
        )

        response = self.client.get(reverse('api-v2:officers-mobile-list'), {'ids': '2,1'})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'id': 2,
                'full_name': 'Ronald Watts',
                'complaint_count': 5,
                'percentile_trr': '0.0000',
                'percentile_allegation': '99.5000',
                'percentile_allegation_civilian': '98.4344',
            },
            {
                'id': 1,
                'full_name': 'Daryl Mack',
                'complaint_count': 12,
                'percentile_allegation': '99.3450',
                'percentile_allegation_civilian': '99.7840',
                'percentile_allegation_internal': '99.7840',
                'percentile_trr': '12.0000',
            }
        ])

    def test_new_timeline_item_with_officer_alias(self):
        officer = OfficerFactory(id=456, appointed_date=date(2000, 1, 1))
        OfficerAliasFactory(old_officer_id=123, new_officer=officer)
        unit = PoliceUnitFactory(unit_name='001', description='unit_001')
        OfficerHistoryFactory(officer=officer, unit=unit, effective_date=date(2010, 1, 1), end_date=date(2011, 12, 31))
        AwardFactory(officer=officer, start_date=date(2011, 3, 23), award_type='Life Saving Award')

        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-mobile-new-timeline-items', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'unit_name': '001',
                'kind': 'AWARD',
                'unit_description': 'unit_001',
                'award_type': 'Life Saving Award',
                'date': '2011-03-23'
            },
            {
                'unit_name': '001',
                'kind': 'UNIT_CHANGE',
                'unit_description': 'unit_001',
                'date': '2010-01-01'
            },
            {
                'unit_name': '',
                'kind': 'JOINED',
                'unit_description': '',
                'date': '2000-01-01'
            }
        ])

    def test_coaccusals(self):
        officer1 = OfficerFactory(
            appointed_date=date(2001, 1, 1),
            allegation_count=2,
            sustained_count=0,
        )
        officer2 = OfficerFactory(
            first_name='Jerome',
            last_name='Finnigan',
            race='White',
            gender='M',
            birth_year=1950,
            rank='Police Officer',
            appointed_date=date(2002, 1, 1),
            complaint_percentile=95.0,
            civilian_allegation_percentile=33.3333,
            internal_allegation_percentile=0.0,
            trr_percentile=33.3333,
            allegation_count=2,
            sustained_count=1,
        )
        officer3 = OfficerFactory(
            first_name='Officer',
            last_name='2',
            race='Black',
            gender='M',
            birth_year=1970,
            rank='Police Officer',
            appointed_date=date(2003, 1, 1),
            complaint_percentile=99.0,
            civilian_allegation_percentile=66.6667,
            internal_allegation_percentile=0.0,
            trr_percentile=66.6667,
            allegation_count=1,
            sustained_count=1,
        )
        officer4 = OfficerFactory(
            first_name='Edward',
            last_name='May',
            race='White',
            gender='F',
            birth_year=1950,
            rank='Detective',
            appointed_date=None,
            complaint_percentile=None,
            allegation_count=1,
            sustained_count=0,
        )
        allegation1 = AllegationFactory(incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc))
        allegation2 = AllegationFactory(incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc))
        allegation3 = AllegationFactory(incident_date=datetime(2005, 1, 1, tzinfo=pytz.utc))
        allegation4 = AllegationFactory(incident_date=datetime(2005, 1, 1, tzinfo=pytz.utc))
        OfficerAllegationFactory(
            officer=officer2, allegation=allegation1, final_finding='SU', start_date=date(2003, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation2, final_finding='SU', start_date=date(2004, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer1, allegation=allegation3, final_finding='NS', start_date=date(2006, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer2, allegation=allegation3, final_finding='NS', start_date=date(2006, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer4, allegation=allegation4, final_finding='NS', start_date=date(2007, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer1, allegation=allegation4, final_finding='NS', start_date=date(2007, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer2, allegation=allegation4, final_finding='NS', start_date=date(2007, 1, 1)
        )

        expected_response_data = [{
            'id': officer2.id,
            'full_name': 'Jerome Finnigan',
            'rank': 'Police Officer',
            'coaccusal_count': 2,
            'percentile_allegation': '95.0000',
            'percentile_allegation_civilian': '33.3333',
            'percentile_allegation_internal': '0.0000',
            'percentile_trr': '33.3333',
        }, {
            'id': officer4.id,
            'full_name': 'Edward May',
            'coaccusal_count': 1,
            'rank': 'Detective',
        }]
        response = self.client.get(reverse('api-v2:officers-mobile-coaccusals', kwargs={'pk': officer1.id}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_response_data)
