import json
from datetime import date, datetime

from django.contrib.gis.geos import Point
from django.utils.http import urlencode
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

import pytz
import botocore
from mock import patch
from robber import expect

from data.constants import ACTIVE_YES_CHOICE
from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, PoliceUnitFactory,
    AllegationCategoryFactory, OfficerHistoryFactory, OfficerBadgeNumberFactory, AwardFactory, ComplainantFactory,
    SalaryFactory, OfficerAliasFactory, VictimFactory,
    InvestigatorFactory,
    InvestigatorAllegationFactory,
    AttachmentFileFactory,
)
from trr.factories import TRRFactory
from officers.tests.mixins import OfficerSummaryTestCaseMixin
from data.cache_managers import officer_cache_manager, allegation_cache_manager
from data import cache_managers


class OfficersViewSetTestCase(OfficerSummaryTestCaseMixin, APITestCase):
    def test_summary(self):
        officer = OfficerFactory(
            tags=[],
            first_name='Kevin', last_name='Kerl', id=123, race='White', gender='M',
            appointed_date=date(2017, 2, 27), rank='PO', resignation_date=date(2017, 12, 27),
            active=ACTIVE_YES_CHOICE, birth_year=1910, complaint_percentile=32.5,
            sustained_count=1, allegation_count=1, discipline_count=1, trr_count=1,
            civilian_compliment_count=1, honorable_mention_count=1, major_award_count=1,
            last_unit_id=1, current_badge='123456', current_salary=90000, has_unique_name=True
        )
        allegation = AllegationFactory()
        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerHistoryFactory(officer=officer, unit=PoliceUnitFactory(id=1, unit_name='CAND', description=''))
        ComplainantFactory(allegation=allegation, race='White', age=18, gender='F')
        OfficerBadgeNumberFactory(officer=officer, star='123456', current=True)
        OfficerAllegationFactory(
            officer=officer, allegation=allegation, allegation_category=allegation_category,
            final_finding='SU', start_date=date(2000, 1, 1), disciplined=True
        )
        AwardFactory(officer=officer, award_type='Complimentary Letter')
        AwardFactory(officer=officer, award_type='Honored Police Star')
        AwardFactory(officer=officer, award_type='Honorable Mention')
        SalaryFactory(officer=officer, salary=50000, year=2015)
        SalaryFactory(officer=officer, salary=90000, year=2017)
        TRRFactory(officer=officer)

        officer_cache_manager.build_cached_columns()
        allegation_cache_manager.cache_data()

        response = self.client.get(reverse('api-v2:officers-summary', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expected_data = {
            'id': 123,
            'unit': {
                'id': 1,
                'unit_name': 'CAND',
                'description': '',
                'long_unit_name': 'Unit CAND',
            },
            'date_of_appt': '2017-02-27',
            'date_of_resignation': '2017-12-27',
            'active': 'Active',
            'rank': 'PO',
            'full_name': 'Kevin Kerl',
            'race': 'White',
            'badge': '123456',
            'historic_units': [{
                'id': 1,
                'unit_name': 'CAND',
                'description': '',
                'long_unit_name': 'Unit CAND'
            }],
            'gender': 'Male',
            'birth_year': 1910,
            'sustained_count': 1,
            'civilian_compliment_count': 1,
            'allegation_count': 1,
            'discipline_count': 1,
            'honorable_mention_count': 1,
            'to': '/officer/123/kevin-kerl/',
            'url': 'http://cpdb.lvh.me/officer/kevin-kerl/123',
            'current_salary': 90000,
            'trr_count': 1,
            'major_award_count': 1,
            'unsustained_count': 0,
            'complaint_percentile': 32.5,
            'coaccusals': [],
            'percentiles': [],
            'tags': [],
            'historic_badges': [],
            'has_unique_name': True
        }
        expect(response.data).to.eq(expected_data)

    def test_summary_no_match(self):
        response = self.client.get(reverse('api-v2:officers-summary', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_summary_with_alias(self):
        officer = OfficerFactory(id=456)
        OfficerAliasFactory(old_officer_id=123, new_officer=officer)
        response = self.client.get(reverse('api-v2:officers-summary', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['id']).to.eq(456)

    def test_new_timeline_items_no_match(self):
        response = self.client.get(reverse('api-v2:officers-new-timeline-items', kwargs={'pk': 456}))
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

        response = self.client.get(reverse('api-v2:officers-new-timeline-items', kwargs={'pk': 123}))

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

    def test_new_timeline_item_no_join(self):
        officer = OfficerFactory(id=123, appointed_date=None, rank='Police Officer')

        unit = PoliceUnitFactory(unit_name='001', description='unit_001')
        OfficerHistoryFactory(officer=officer, unit=unit, effective_date=date(2010, 1, 1), end_date=date(2011, 12, 31))

        allegation = AllegationFactory(
            crid='123456',
            coaccused_count=4,
            incident_date=datetime(2011, 8, 23, tzinfo=pytz.utc)
        )
        OfficerAllegationFactory(
            final_finding='UN', final_outcome='Unknown',
            officer=officer, allegation=allegation,
            allegation_category=AllegationCategoryFactory(category='category', allegation_name='sub category')
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)

        SalaryFactory(officer=officer, year=2001, rank='Police Officer', spp_date=date(2001, 9, 23))

        cache_managers.cache_all()

        response = self.client.get(reverse('api-v2:officers-new-timeline-items', kwargs={'pk': 123}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
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
                'victims': [],
                'attachments': [],
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
            }
        ])

    def test_new_timeline_item_merge_rank_and_unit_change_join(self):
        officer = OfficerFactory(id=123, appointed_date=date(2000, 1, 1), rank='Police Officer')

        first_unit = PoliceUnitFactory(unit_name='001', description='unit_001')
        unit = PoliceUnitFactory(unit_name='002', description='unit_002')
        OfficerHistoryFactory(
            officer=officer,
            unit=first_unit,
            effective_date=date(2000, 1, 1),
            end_date=date(2009, 12, 31))
        OfficerHistoryFactory(
            officer=officer,
            unit=unit,
            effective_date=date(2010, 1, 1),
            end_date=date(2011, 12, 31))

        SalaryFactory(officer=officer, year=2001, rank='Police Officer', spp_date=date(2001, 9, 23))
        SalaryFactory(officer=officer, year=2000, rank='Junior Police Officer', spp_date=date(2000, 1, 1))

        cache_managers.cache_all()

        response = self.client.get(reverse('api-v2:officers-new-timeline-items', kwargs={'pk': 123}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'date': '2010-01-01',
                'kind': 'UNIT_CHANGE',
                'unit_name': '002',
                'unit_description': 'unit_002',
                'rank': 'Police Officer',
            }, {
                'date': '2001-09-23',
                'kind': 'RANK_CHANGE',
                'unit_name': '001',
                'unit_description': 'unit_001',
                'rank': 'Police Officer',
            }, {
                'date': '2000-01-01',
                'kind': 'JOINED',
                'unit_name': '001',
                'unit_description': 'unit_001',
                'rank': 'Junior Police Officer',
            }
        ])

    def test_new_timeline_item_with_alias(self):
        officer = OfficerFactory(id=456, appointed_date=date(2000, 1, 1))
        OfficerAliasFactory(old_officer_id=123, new_officer=officer)
        unit = PoliceUnitFactory(unit_name='001', description='unit_001')
        OfficerHistoryFactory(officer=officer, unit=unit, effective_date=date(2010, 1, 1), end_date=date(2011, 12, 31))
        AwardFactory(officer=officer, start_date=date(2011, 3, 23), award_type='Life Saving Award')

        response = self.client.get(reverse('api-v2:officers-new-timeline-items', kwargs={'pk': 123}))
        expect(response.data).to.eq([
            {
                'date': '2011-03-23',
                'kind': 'AWARD',
                'award_type': 'Life Saving Award',
                'unit_name': '001',
                'unit_description': 'unit_001'
            },
            {
                'date': '2010-01-01',
                'kind': 'UNIT_CHANGE',
                'unit_name': '001',
                'unit_description': 'unit_001'
            },
            {
                'date': '2000-01-01',
                'kind': 'JOINED',
                'unit_name': '',
                'unit_description': ''
            }
        ])

    def test_top_officers_by_allegation(self):
        OfficerFactory(
            id=1, first_name='Daryl', last_name='Mack',
            trr_percentile=12.0000,
            civilian_allegation_percentile=98.4344,
            internal_allegation_percentile=99.7840,
            complaint_percentile=99.3450,
            race='White', gender='M', birth_year=1975,
            rank='Police Officer'
        )
        OfficerFactory(
            id=2,
            first_name='Ronald', last_name='Watts',
            trr_percentile=0.0000,
            civilian_allegation_percentile=98.4344,
            internal_allegation_percentile=99.7840,
            complaint_percentile=99.5000,
            race='White', gender='M', birth_year=1975,
            rank='Detective'
        )
        OfficerFactory(
            id=3,
            first_name='Officer', last_name='low percentile',
            trr_percentile=0.0000,
            civilian_allegation_percentile=0.0000,
            internal_allegation_percentile=0.0000,
            complaint_percentile=96.3450,
            race='White', gender='M', birth_year=1975,
            rank=''
        )
        OfficerFactory(
            id=4,
            first_name='Officer', last_name='no visual token',
            trr_percentile=0.0000,
            internal_allegation_percentile=0.0000,
            complaint_percentile=99.8800,
            race='White', gender='M', birth_year=1975,
            rank='Police Officer'
        )
        OfficerFactory(
            id=5,
            first_name='Officer', last_name='filter out',
            trr_percentile=0.0000,
            civilian_allegation_percentile=0.0000,
            internal_allegation_percentile=0.0000,
            complaint_percentile=99.2000,
            race='White', gender='M', birth_year=1975,
            rank='Detective'
        )
        OfficerFactory(
            id=6,
            first_name='Officer', last_name='no percentiles',
            complaint_percentile=99.8000,
            race='White', gender='M', birth_year=1975,
            rank='Police Officer'
        )

        officer_cache_manager.build_cached_columns()
        allegation_cache_manager.cache_data()

        response = self.client.get(reverse('api-v2:officers-top-by-allegation'), {'limit': 2})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.have.length(2)
        expect(response.data).to.eq([{
            'id': 2,
            'full_name': 'Ronald Watts',
            'complaint_count': 0,
            'sustained_count': 0,
            'birth_year': 1975,
            'complaint_percentile': 99.5000,
            'race': 'White',
            'gender': 'Male',
            'rank': 'Detective',
            'percentile': {
                'percentile_trr': '0.0000',
                'percentile_allegation': '99.5000',
                'percentile_allegation_civilian': '98.4344',
                'percentile_allegation_internal': '99.7840',
                'year': 2016,
                'id': 2,
            },
        }, {
            'id': 1,
            'full_name': 'Daryl Mack',
            'complaint_count': 0,
            'sustained_count': 0,
            'birth_year': 1975,
            'complaint_percentile': 99.3450,
            'race': 'White',
            'gender': 'Male',
            'rank': 'Police Officer',
            'percentile': {
                'percentile_trr': '12.0000',
                'percentile_allegation': '99.3450',
                'percentile_allegation_civilian': '98.4344',
                'percentile_allegation_internal': '99.7840',
                'year': 2016,
                'id': 1,
            },
        }])

    def test_coaccusals_not_found(self):
        response_not_found = self.client.get(reverse('api-v2:officers-coaccusals', kwargs={'pk': 999}))
        expect(response_not_found.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_coaccusals(self):
        officer1 = OfficerFactory(
            appointed_date=date(2001, 1, 1),
            allegation_count=2,
            sustained_count=0,
        )
        officer2 = OfficerFactory(
            first_name='Officer',
            last_name='1',
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
            first_name='Officer',
            last_name='No Percentile',
            race='White',
            gender='F',
            birth_year=1950,
            rank='Police Officer',
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
            'full_name': 'Officer 1',
            'complaint_count': 2,
            'sustained_count': 1,
            'birth_year': 1950,
            'complaint_percentile': 95.0,
            'race': 'White',
            'gender': 'Male',
            'rank': 'Police Officer',
            'coaccusal_count': 2,
            'percentile': {
                'percentile_trr': '33.3333',
                'percentile_allegation': '95.0000',
                'percentile_allegation_civilian': '33.3333',
                'percentile_allegation_internal': '0.0000',
                'id': officer2.id,
                'year': 2016
            },
        }, {
            'id': officer4.id,
            'full_name': 'Officer No Percentile',
            'complaint_count': 1,
            'sustained_count': 0,
            'birth_year': 1950,
            'race': 'White',
            'gender': 'Female',
            'coaccusal_count': 1,
            'rank': 'Police Officer',
            'percentile': {
                'id': officer4.id,
                'year': 2016
            },
        }]
        response = self.client.get(reverse('api-v2:officers-coaccusals', kwargs={'pk': officer1.id}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq(expected_response_data)

    def test_list_all_invalid_ids(self):
        response = self.client.get(reverse('api-v2:officers-list'), {'ids': '1,2.0,3'})
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
            rank='Police Officer',
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
            rank='Police Officer',
        )

        response = self.client.get(reverse('api-v2:officers-list'), {'ids': '2,1'})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'id': 2,
                'full_name': 'Ronald Watts',
                'birth_year': 1971,
                'complaint_count': 5,
                'complaint_percentile': 99.5,
                'race': 'Black',
                'gender': 'Female',
                'rank': 'Police Officer',
                'percentile': {
                    'id': 2,
                    'year': 2016,
                    'percentile_trr': '0.0000',
                    'percentile_allegation': '99.5000',
                    'percentile_allegation_civilian': '98.4344',
                }
            },
            {
                'id': 1,
                'full_name': 'Daryl Mack',
                'complaint_count': 12,
                'sustained_count': 0,
                'birth_year': 1975,
                'complaint_percentile': 99.3450,
                'race': 'White',
                'gender': 'Male',
                'rank': 'Police Officer',
                'percentile': {
                    'id': 1,
                    'year': 2016,
                    'percentile_trr': '12.0000',
                    'percentile_allegation': '99.3450',
                    'percentile_allegation_civilian': '99.7840',
                    'percentile_allegation_internal': '99.7840'
                }
            }
        ])

    def test_coaccusals_with_alias(self):
        officer = OfficerFactory(id=456)
        OfficerAliasFactory(old_officer_id=123, new_officer=officer)
        allegation = AllegationFactory()
        coaccused = OfficerFactory(id=333)
        OfficerAllegationFactory(officer=officer, allegation=allegation)
        OfficerAllegationFactory(officer=coaccused, allegation=allegation)

        response = self.client.get(reverse('api-v2:officers-coaccusals', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data[0]['id']).to.eq(333)

    @override_settings(S3_BUCKET_ZIP_DIRECTORY='zip', S3_BUCKET_OFFICER_CONTENT='officer_content_bucket')
    @patch('data.models.officer.aws')
    def test_request_download_no_match(self, _):
        base_url = reverse('api-v2:officers-request-download', kwargs={'pk': 123})
        query = urlencode({'with-docs': 'true'})
        response = self.client.get(f'{base_url}?{query}')
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    @override_settings(S3_BUCKET_ZIP_DIRECTORY='zip', S3_BUCKET_OFFICER_CONTENT='officer_content_bucket')
    @patch('data.models.officer.aws')
    def test_request_download(self, aws_mock):
        aws_mock.s3.get_object.return_value = {}
        aws_mock.s3.generate_presigned_url.return_value = 'presigned_url'

        OfficerFactory(id=123)

        base_url = reverse('api-v2:officers-request-download', kwargs={'pk': 123})
        query = urlencode({'with-docs': 'true'})
        response = self.client.get(f'{base_url}?{query}')

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq('presigned_url')
        aws_mock.s3.get_object.assert_called_with(
            Bucket='officer_content_bucket',
            Key='zip_with_docs/Officer_123_with_docs.zip'
        )
        aws_mock.s3.generate_presigned_url.assert_called_with(
            ClientMethod='get_object',
            Params={
                'Bucket': 'officer_content_bucket',
                'Key': 'zip_with_docs/Officer_123_with_docs.zip',
            }
        )

    @override_settings(S3_BUCKET_ZIP_DIRECTORY='zip', S3_BUCKET_OFFICER_CONTENT='officer_content_bucket')
    @patch('data.models.officer.aws')
    def test_request_download_file_not_exist(self, aws_mock):
        exception = botocore.exceptions.ClientError(
            error_response={'Error': {'Code': 'NoSuchKey'}},
            operation_name='get_object'
        )
        aws_mock.s3.get_object.side_effect = exception
        aws_mock.s3.generate_presigned_url.return_value = 'presigned_url'

        OfficerFactory(id=123)

        base_url = reverse('api-v2:officers-request-download', kwargs={'pk': 123})
        query = urlencode({'with-docs': 'true'})
        response = self.client.get(f'{base_url}?{query}')

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq('')
        aws_mock.s3.get_object.assert_called_with(
            Bucket='officer_content_bucket',
            Key='zip_with_docs/Officer_123_with_docs.zip'
        )
        expect(aws_mock.s3.generate_presigned_url.called).to.be.false()

    @override_settings(S3_BUCKET_ZIP_DIRECTORY='zip', S3_BUCKET_OFFICER_CONTENT='officer_content_bucket')
    @patch('data.models.officer.aws')
    def test_request_download_without_docs(self, aws_mock):
        aws_mock.s3.get_object.return_value = {}
        aws_mock.s3.generate_presigned_url.return_value = 'presigned_url'

        OfficerFactory(id=123)

        base_url = reverse('api-v2:officers-request-download', kwargs={'pk': 123})
        query = urlencode({'with-docs': 'false'})
        response = self.client.get(f'{base_url}?{query}')

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq('presigned_url')
        aws_mock.s3.get_object.assert_called_with(
            Bucket='officer_content_bucket',
            Key='zip/Officer_123.zip'
        )
        aws_mock.s3.generate_presigned_url.assert_called_with(
            ClientMethod='get_object',
            Params={
                'Bucket': 'officer_content_bucket',
                'Key': 'zip/Officer_123.zip',
            }
        )

    @override_settings(
        S3_BUCKET_OFFICER_CONTENT='officer_content_bucket',
        S3_BUCKET_ZIP_DIRECTORY='zip',
        S3_BUCKET_XLSX_DIRECTORY='xlsx',
        S3_BUCKET_PDF_DIRECTORY='pdf'
    )
    @patch('data.models.officer.aws')
    def test_create_zip_file_no_match(self, _):
        response = self.client.get(reverse('api-v2:officers-create-zip-file', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    @override_settings(
        S3_BUCKET_OFFICER_CONTENT='officer_content_bucket',
        S3_BUCKET_ZIP_DIRECTORY='zip',
        S3_BUCKET_XLSX_DIRECTORY='xlsx',
        S3_BUCKET_PDF_DIRECTORY='pdf',
        LAMBDA_FUNCTION_CREATE_OFFICER_ZIP_FILE='createOfficerZipFileTest'
    )
    @patch('data.models.officer.aws')
    def test_create_zip_file(self, aws_mock):
        exception = botocore.exceptions.ClientError(
            error_response={'Error': {'Code': 'NoSuchKey'}},
            operation_name='get_object'
        )
        aws_mock.s3.get_object.side_effect = exception

        allegation = AllegationFactory(crid='1')
        allegation_456 = AllegationFactory(crid='456')

        AttachmentFileFactory(
            allegation=allegation,
            source_type='DOCUMENTCLOUD',
            external_id='ABC',
            title='allegation 1 attachment'
        )
        AttachmentFileFactory(allegation=allegation, source_type='COPA')
        AttachmentFileFactory(allegation=allegation_456, source_type='DOCUMENTCLOUD')
        AttachmentFileFactory(allegation=allegation_456, source_type='COPA_DOCUMENTCLOUD')

        officer = OfficerFactory(id=1)
        OfficerAllegationFactory(officer=officer, allegation=allegation)

        allegation_2 = AllegationFactory(crid='2')
        allegation_789 = AllegationFactory(crid='789')
        AttachmentFileFactory(
            allegation=allegation_2,
            source_type='DOCUMENTCLOUD',
            external_id='XYZ',
            title='allegation 2 attachment'
        )
        AttachmentFileFactory(allegation=allegation_2, source_type='COPA')
        AttachmentFileFactory(allegation=allegation_789, source_type='DOCUMENTCLOUD')
        AttachmentFileFactory(allegation=allegation_789, source_type='COPA_DOCUMENTCLOUD')

        investigator = InvestigatorFactory(officer=officer)
        InvestigatorAllegationFactory(allegation=allegation_2, investigator=investigator)

        self.client.get(reverse('api-v2:officers-create-zip-file', kwargs={'pk': 1}))

        aws_mock.s3.get_object.assert_any_call(
            Bucket='officer_content_bucket',
            Key='zip_with_docs/Officer_1_with_docs.zip'
        )

        _, kwargs = aws_mock.lambda_client.invoke_async.call_args_list[0]
        expect(kwargs['FunctionName']).to.eq('createOfficerZipFileTest')
        expect(json.loads(kwargs['InvokeArgs'])).to.eq({
            'key': 'zip_with_docs/Officer_1_with_docs.zip',
            'bucket': 'officer_content_bucket',
            'file_map': {
                'xlsx/1/accused.xlsx': 'accused.xlsx',
                'xlsx/1/use_of_force.xlsx': 'use_of_force.xlsx',
                'xlsx/1/investigator.xlsx': 'investigator.xlsx',
                'xlsx/1/documents.xlsx': 'documents.xlsx',
                'pdf/ABC': f'documents/allegation 1 attachment.pdf',
                'pdf/XYZ': f'investigators/allegation 2 attachment.pdf'
            }
        })

        aws_mock.s3.get_object.assert_any_call(
            Bucket='officer_content_bucket',
            Key='zip/Officer_1.zip'
        )

        _, kwargs = aws_mock.lambda_client.invoke_async.call_args_list[1]
        expect(kwargs['FunctionName']).to.eq('createOfficerZipFileTest')
        expect(json.loads(kwargs['InvokeArgs'])).to.eq({
            'key': 'zip/Officer_1.zip',
            'bucket': 'officer_content_bucket',
            'file_map': {
                'xlsx/1/accused.xlsx': 'accused.xlsx',
                'xlsx/1/use_of_force.xlsx': 'use_of_force.xlsx',
                'xlsx/1/investigator.xlsx': 'investigator.xlsx',
                'xlsx/1/documents.xlsx': 'documents.xlsx',
            }
        })

    @override_settings(
        S3_BUCKET_OFFICER_CONTENT='officer_content_bucket',
        S3_BUCKET_ZIP_DIRECTORY='zip',
        S3_BUCKET_XLSX_DIRECTORY='xlsx',
        S3_BUCKET_PDF_DIRECTORY='pdf',
        LAMBDA_FUNCTION_CREATE_OFFICER_ZIP_FILE='createOfficerZipFileTest'
    )
    @patch('data.models.officer.aws')
    def test_create_zip_file_already_exist(self, aws_mock):
        aws_mock.s3.get_object.return_value = {}

        allegation = AllegationFactory(crid='1')
        allegation_456 = AllegationFactory(crid='456')

        AttachmentFileFactory(
            allegation=allegation,
            source_type='DOCUMENTCLOUD',
            external_id='ABC',
            title='allegation 1 attachment'
        )
        AttachmentFileFactory(allegation=allegation, source_type='COPA')
        AttachmentFileFactory(allegation=allegation_456, source_type='DOCUMENTCLOUD')
        AttachmentFileFactory(allegation=allegation_456, source_type='COPA_DOCUMENTCLOUD')

        officer = OfficerFactory(id=1)
        OfficerAllegationFactory(officer=officer, allegation=allegation)

        allegation_2 = AllegationFactory(crid='2')
        allegation_789 = AllegationFactory(crid='789')
        AttachmentFileFactory(
            allegation=allegation_2,
            source_type='DOCUMENTCLOUD',
            external_id='XYZ',
            title='allegation 2 attachment'
        )
        AttachmentFileFactory(allegation=allegation_2, source_type='COPA')
        AttachmentFileFactory(allegation=allegation_789, source_type='DOCUMENTCLOUD')
        AttachmentFileFactory(allegation=allegation_789, source_type='COPA_DOCUMENTCLOUD')

        investigator = InvestigatorFactory(officer=officer)
        InvestigatorAllegationFactory(allegation=allegation_2, investigator=investigator)

        self.client.get(reverse('api-v2:officers-create-zip-file', kwargs={'pk': 1}))

        aws_mock.s3.get_object.assert_any_call(
            Bucket='officer_content_bucket',
            Key='zip_with_docs/Officer_1_with_docs.zip'
        )
        aws_mock.s3.get_object.assert_any_call(
            Bucket='officer_content_bucket',
            Key='zip/Officer_1.zip'
        )
        expect(aws_mock.lambda_client.invoke_async.called).to.be.false()
