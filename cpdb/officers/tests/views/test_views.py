from datetime import date, datetime

from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from robber import expect
import pytz

from data.constants import ACTIVE_YES_CHOICE
from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, PoliceUnitFactory,
    AllegationCategoryFactory, OfficerHistoryFactory, OfficerBadgeNumberFactory, AwardFactory, ComplainantFactory,
    SalaryFactory,
    VictimFactory,
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
            last_unit_id=1, current_badge='123456', current_salary=90000
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
        }
        expect(response.data).to.eq(expected_data)

    def test_summary_no_match(self):
        response = self.client.get(reverse('api-v2:officers-summary', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

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
        allegation = AllegationFactory(crid='123456', coaccused_count=4)
        VictimFactory(allegation=allegation, gender='M', race='White', age=34)
        OfficerAllegationFactory(
            final_finding='UN', final_outcome='Unknown',
            officer=officer, start_date=date(2011, 8, 23), allegation=allegation,
            allegation_category=AllegationCategoryFactory(category='category', allegation_name='sub category')
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)

        allegation2 = AllegationFactory(crid='654321', point=Point(35.5, 68.9), coaccused_count=1)
        OfficerAllegationFactory(
            final_finding='UN', final_outcome='9 Day Suspension',
            officer=officer, start_date=date(2015, 8, 23), allegation=allegation2,
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

        allegation = AllegationFactory(crid='123456', coaccused_count=4)
        OfficerAllegationFactory(
            final_finding='UN', final_outcome='Unknown',
            officer=officer, start_date=date(2011, 8, 23), allegation=allegation,
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

    def test_top_officers_by_allegation(self):
        OfficerFactory(
            id=1, first_name='Daryl', last_name='Mack',
            trr_percentile=12.0000,
            civilian_allegation_percentile=98.4344,
            internal_allegation_percentile=99.7840,
            complaint_percentile=99.3450,
            race='White', gender='M', birth_year=1975,
        )
        OfficerFactory(
            id=2,
            first_name='Ronald', last_name='Watts',
            trr_percentile=0.0000,
            civilian_allegation_percentile=98.4344,
            internal_allegation_percentile=99.7840,
            complaint_percentile=99.5000,
            race='White', gender='M', birth_year=1975,
        )
        OfficerFactory(
            id=3,
            first_name='Officer', last_name='low percentile',
            trr_percentile=0.0000,
            civilian_allegation_percentile=0.0000,
            internal_allegation_percentile=0.0000,
            complaint_percentile=96.3450,
            race='White', gender='M', birth_year=1975,
        )
        OfficerFactory(
            id=4,
            first_name='Officer', last_name='no visual token',
            trr_percentile=0.0000,
            internal_allegation_percentile=0.0000,
            complaint_percentile=99.8800,
            race='White', gender='M', birth_year=1975,
        )
        OfficerFactory(
            id=5,
            first_name='Officer', last_name='filter out',
            trr_percentile=0.0000,
            civilian_allegation_percentile=0.0000,
            internal_allegation_percentile=0.0000,
            complaint_percentile=99.2000,
            race='White', gender='M', birth_year=1975,
        )
        OfficerFactory(
            id=6,
            first_name='Officer', last_name='no percentiles',
            complaint_percentile=99.8000,
            race='White', gender='M', birth_year=1975,
        )

        officer_cache_manager.build_cached_columns()
        allegation_cache_manager.cache_data()

        response = self.client.get(reverse('api-v2:officers-top-by-allegation'), {'limit': 2})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.have.length(2)
        expect(response.data).to.eq([
            {
                'complaint_percentile': 99.5000,
                'full_name': u'Ronald Watts',
                'id': 2,
                'percentile': {
                    u'percentile_trr': '0.0000',
                    u'percentile_allegation': '99.5000',
                    u'percentile_allegation_civilian': '98.4344',
                    u'percentile_allegation_internal': '99.7840',
                    u'year': 2016,
                    u'id': 2,
                },
                'race': u'White',
                'gender': u'Male',
                'complaint_count': 0,
                'sustained_count': 0,
                'birth_year': 1975,
            },
            {
                'complaint_percentile': 99.3450,
                'full_name': u'Daryl Mack',
                'id': 1,
                'percentile': {
                    u'percentile_trr': '12.0000',
                    u'percentile_allegation': '99.3450',
                    u'percentile_allegation_civilian': '98.4344',
                    u'percentile_allegation_internal': '99.7840',
                    u'year': 2016,
                    u'id': 1,
                },
                'race': u'White',
                'gender': u'Male',
                'complaint_count': 0,
                'sustained_count': 0,
                'birth_year': 1975,
            }
        ])

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

        response = self.client.get(reverse('api-v2:officers-coaccusals', kwargs={'pk': officer1.id}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expected_response_data = [{
            'id': officer2.id,
            'full_name': 'Officer 1',
            'allegation_count': 2,
            'sustained_count': 1,
            'race': 'White',
            'gender': 'Male',
            'birth_year': 1950,
            'coaccusal_count': 2,
            'rank': 'Police Officer',
            'complaint_percentile': 95.0,
            'percentile_trr': 33.3333,
            'percentile_allegation_civilian': 33.3333,
            'percentile_allegation_internal': 0.0,
        }, {
            'id': officer4.id,
            'full_name': 'Officer No Percentile',
            'allegation_count': 1,
            'sustained_count': 0,
            'race': 'White',
            'gender': 'Female',
            'birth_year': 1950,
            'coaccusal_count': 1,
            'rank': 'Police Officer',
        }]
        expect(response.data).to.eq(expected_response_data)
