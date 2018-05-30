from datetime import date, datetime

import pytz
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from robber import expect

from data.constants import ACTIVE_YES_CHOICE
from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, PoliceUnitFactory,
    AllegationCategoryFactory, OfficerHistoryFactory, OfficerBadgeNumberFactory, AwardFactory, ComplainantFactory,
    SalaryFactory
)
from officers.doc_types import OfficerInfoDocType
from trr.factories import TRRFactory
from .mixins import OfficerSummaryTestCaseMixin


class OfficersViewSetTestCase(OfficerSummaryTestCaseMixin, APITestCase):
    def test_summary(self):
        officer = OfficerFactory(
            tags=[],
            first_name='Kevin', last_name='Kerl', id=123, race='White', gender='M',
            appointed_date=date(2017, 2, 27), rank='PO', resignation_date=date(2017, 12, 27),
            active=ACTIVE_YES_CHOICE, birth_year=1910
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

        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-summary', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 123,
            'unit': {
                'id': 1,
                'unit_name': 'CAND',
                'description': '',
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
            }],
            'gender': 'Male',
            'complaint_records': {
                'count': 1,
                'sustained_count': 1,
                'items': [{'count': 1, 'sustained_count': 1, 'year': 2000}],
                'facets': [
                    {
                        'name': 'category',
                        'entries': [{'name': 'Use of Force', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': 'Use of Force', 'count': 1, 'sustained_count': 1}
                        ]}]
                    },
                    {
                        'name': 'complainant race',
                        'entries': [{'name': 'White', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': 'White', 'count': 1, 'sustained_count': 1}
                        ]}]
                    },
                    {
                        'name': 'complainant age',
                        'entries': [{'name': '<20', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': '<20', 'count': 1, 'sustained_count': 1}
                        ]}]
                    },
                    {
                        'name': 'complainant gender',
                        'entries': [{'name': 'Female', 'count': 1, 'sustained_count': 1, 'items': [
                            {'year': 2000, 'name': 'Female', 'count': 1, 'sustained_count': 1}
                        ]}]
                    }
                ]
            },
            'birth_year': 1910,
            'sustained_count': 1,
            'civilian_compliment_count': 1,
            'allegation_count': 1,
            'discipline_count': 1,
            'honorable_mention_count': 1,
            'to': '/officer/123/',
            'url': 'https://beta.cpdb.co/officer/kevin-kerl/123',
            'current_salary': 90000,
            'trr_count': 1,
            'major_award_count': 1,
        })

    def test_summary_no_match(self):
        response = self.client.get(reverse('api-v2:officers-summary', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_timeline_items(self):
        officer = OfficerFactory(id=123, appointed_date=date(2000, 1, 1))
        allegation = AllegationFactory(crid='123456')
        OfficerHistoryFactory(officer=officer, effective_date=date(2017, 2, 27), unit=PoliceUnitFactory(unit_name='A'))
        OfficerAllegationFactory(
            final_finding='UN', officer=officer, start_date=date(2016, 8, 23), allegation=allegation,
            allegation_category=AllegationCategoryFactory(category='category', allegation_name='sub category')
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-timeline-items', kwargs={'pk': 123}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'count': 3,
            'next': None,
            'previous': None,
            'results': [
                {
                    'kind': 'UNIT_CHANGE',
                    'date': '2017-02-27',
                    'unit_name': 'A'
                },
                {
                    'kind': 'CR',
                    'date': '2016-08-23',
                    'crid': '123456',
                    'category': 'category',
                    'subcategory': 'sub category',
                    'finding': 'Unfounded',
                    'coaccused': 4,
                    'race': ['Unknown'],
                    'gender': ['Unknown'],
                    'age': ['Unknown']
                },
                {
                    'kind': 'JOINED',
                    'date': '2000-01-01'
                }
            ]
        })

    def test_timeline_items_filter_params(self):
        officer = OfficerFactory(id=123, appointed_date=date(2000, 1, 1))
        allegation = AllegationFactory(crid='123456')
        OfficerHistoryFactory(officer=officer, effective_date=date(2017, 2, 27), unit=PoliceUnitFactory(unit_name='A'))
        OfficerAllegationFactory(
            final_finding='UN', officer=officer, start_date=date(2016, 8, 23), allegation=allegation,
            allegation_category=AllegationCategoryFactory(category='Illegal Search', allegation_name='sub category')
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)

        allegation2 = AllegationFactory(crid='654321')
        OfficerAllegationFactory(
            final_finding='UN', officer=officer, start_date=date(2017, 8, 23), allegation=allegation2,
            allegation_category=AllegationCategoryFactory(category='Use of Force', allegation_name='sub category')
        )
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-timeline-items', kwargs={'pk': 123}),
                                   data={'category': 'Illegal Search', 'finding': 'Unfounded', 'invalid': 'X'})
        # NOTE: 'finding' and 'invalid' should drop since this is not in ALLOWED LIST

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'count': 3,
            'next': None,
            'previous': None,
            'results': [
                {
                    'kind': 'UNIT_CHANGE',
                    'date': '2017-02-27',
                    'unit_name': 'A'
                }, {
                    'kind': 'CR',
                    'date': '2016-08-23',
                    'crid': '123456',
                    'category': 'Illegal Search',
                    'subcategory': 'sub category',
                    'finding': 'Unfounded',
                    'coaccused': 4,
                    'race': ['Unknown'],
                    'gender': ['Unknown'],
                    'age': ['Unknown']
                }, {
                    'kind': 'JOINED',
                    'date': '2000-01-01'
                }
            ]
        })

    def test_timeline_no_data(self):
        response = self.client.get(reverse('api-v2:officers-timeline-items', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_timeline_next_request_url(self):
        officer = OfficerFactory(id=123, appointed_date=date(2000, 1, 1))
        OfficerHistoryFactory.create_batch(40, officer=officer, effective_date=date(2017, 1, 1))
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-timeline-items', kwargs={'pk': 123}), {'offset': 10})
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data['count']).to.eq(41)
        expect(response.data['next']).to.match(r'.+\?limit=20\&offset=30$')
        expect(response.data['previous']).to.match(r'.+\?limit=20$')
        expect(len(response.data['results'])).to.eq(20)

    def test_timeline_items_sort_asc(self):
        officer = OfficerFactory(id=123, appointed_date=date(2000, 1, 1))
        allegation = AllegationFactory(crid='123456')
        OfficerHistoryFactory(officer=officer, effective_date=date(2017, 2, 27), unit=PoliceUnitFactory(unit_name='A'))
        OfficerAllegationFactory(
            final_finding='UN', officer=officer, start_date=date(2016, 8, 23), allegation=allegation,
            allegation_category=AllegationCategoryFactory(category='category', allegation_name='sub category')
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-timeline-items', kwargs={'pk': 123}), {'sort': 'asc'})

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'count': 3,
            'next': None,
            'previous': None,
            'results': [
                {
                    'kind': 'JOINED',
                    'date': '2000-01-01'
                },
                {
                    'kind': 'CR',
                    'date': '2016-08-23',
                    'crid': '123456',
                    'category': 'category',
                    'subcategory': 'sub category',
                    'finding': 'Unfounded',
                    'coaccused': 4,
                    'race': ['Unknown'],
                    'gender': ['Unknown'],
                    'age': ['Unknown']
                },
                {
                    'kind': 'UNIT_CHANGE',
                    'date': '2017-02-27',
                    'unit_name': 'A'
                }
            ]
        })

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
        allegation = AllegationFactory(crid='123456')
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

        TRRFactory(officer=officer, trr_datetime=datetime(2011, 9, 23), taser=True, firearm_used=False)
        TRRFactory(officer=officer, trr_datetime=datetime(2015, 9, 23), taser=False, firearm_used=False)

        self.refresh_index()
        response = self.client.get(reverse('api-v2:officers-new-timeline-items', kwargs={'pk': 123}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
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
                'date': '2015-03-23',
                'kind': 'AWARD',
                'unit_name': '002',
                'unit_description': 'unit_002',
                'award_type': 'Complimentary Letter',
                'rank': 'Police Officer',
            }, {
                'date': '2012-01-01',
                'kind': 'UNIT_CHANGE',
                'unit_name': '002',
                'unit_description': 'unit_002',
                'rank': 'Police Officer',
            }, {
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
            }, {
                'date': '2011-03-23',
                'kind': 'AWARD',
                'award_type': 'Honorable Mention',
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

    def test_social_graph_success(self):
        officer1 = OfficerFactory(id=1, first_name='Clarence', last_name='Featherwater')
        officer2 = OfficerFactory(id=2, first_name='Raymond', last_name='Piwnicki')
        allegation = AllegationFactory(incident_date=datetime(2001, 1, 1, tzinfo=pytz.utc))
        OfficerAllegationFactory(officer=officer1, allegation=allegation)
        OfficerAllegationFactory(officer=officer2, allegation=allegation)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-social-graph', kwargs={'pk': 1}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'links': [
                {
                    'source': 1,
                    'target': 2,
                    'cr_years': [2001]
                }
            ],
            'nodes': [
                {
                    'id': 1,
                    'name': 'Clarence Featherwater',
                    'cr_years': [2001]
                },
                {
                    'id': 2,
                    'name': 'Raymond Piwnicki',
                    'cr_years': [2001]
                }
            ]
        })

    def test_social_graph_not_found(self):
        officer1 = OfficerFactory(id=1, first_name='Clarence', last_name='Featherwater')
        officer2 = OfficerFactory(id=2, first_name='Raymond', last_name='Piwnicki')
        allegation = AllegationFactory(incident_date=datetime(2001, 1, 1, tzinfo=pytz.utc))
        OfficerAllegationFactory(officer=officer1, allegation=allegation)
        OfficerAllegationFactory(officer=officer2, allegation=allegation)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-social-graph', kwargs={'pk': 3}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_top_officers_by_allegation(self):
        self.refresh_index()
        OfficerInfoDocType(
            id=1,
            full_name='Alex Mack',
            race='White',
            gender='Male',
            birth_year=1910,
            allegation_count=2,
            complaint_percentile=99.8,
            sustained_count=1,
            percentiles=[
                {
                    'percentile_allegation': 99.345,
                    'percentile_trr': 0.000,
                    'year': 2001,
                    'id': 1,
                    'percentile_allegation_civilian': 98.434,
                    'percentile_allegation_internal': 99.784,
                },
                {
                    'percentile_allegation': 99.345,
                    'percentile_trr': 0.000,
                    'year': 2002,
                    'id': 1,
                    'percentile_allegation_civilian': 98.434,
                    'percentile_allegation_internal': 99.784,
                },
            ]
        ).save()
        OfficerInfoDocType(
            id=2,
            full_name='Ronald Watts',
            race='White',
            gender='Male',
            birth_year=1920,
            allegation_count=2,
            complaint_percentile=99.8,
            sustained_count=1,
            percentiles=[
                {
                    'percentile_allegation': 99.345,
                    'percentile_trr': 0.000,
                    'year': 2001,
                    'id': 2,
                    'percentile_allegation_civilian': 98.0,
                    'percentile_allegation_internal': 99.0,
                },
                {
                    'percentile_allegation': 67.345,
                    'percentile_trr': 0.000,
                    'year': 2002,
                    'id': 2,
                    'percentile_allegation_civilian': 98.434,
                    'percentile_allegation_internal': 99.784,
                },
            ]
        ).save()
        self.refresh_read_index()

        response = self.client.get(reverse('api-v2:officers-top-by-allegation'))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'complaint_percentile': 99.345,
                'race': u'White',
                'gender': u'Male',
                'complaint_count': 2,
                'full_name': u'Alex Mack',
                'sustained_count': 1,
                'id': 1,
                'birth_year': 1910,
                'percentile': {
                    u'percentile_trr': 0.0,
                    u'percentile_allegation_civilian': 98.434,
                    u'percentile_allegation': 99.345,
                    u'year': 2002,
                    u'id': 1,
                    u'percentile_allegation_internal': 99.784
                },
            }
        ])

    def test_coaccusals_not_found(self):
        response_not_found = self.client.get(reverse('api-v2:officers-coaccusals', kwargs={'pk': 999}))
        expect(response_not_found.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_coaccusals(self):
        officer0 = OfficerFactory()
        officer1 = OfficerFactory(
            first_name='Officer',
            last_name='1',
            complaint_percentile=95.0,
            race='White',
            gender='M',
            birth_year=1950,
            rank='Police Officer',
        )
        officer2 = OfficerFactory(
            first_name='Officer',
            last_name='2',
            complaint_percentile=99.0,
            race='Black',
            gender='M',
            birth_year=1970,
            rank='Police Officer',
        )
        allegation0 = AllegationFactory()
        allegation1 = AllegationFactory()
        allegation2 = AllegationFactory()
        OfficerAllegationFactory(officer=officer0, allegation=allegation0, final_finding='SU')
        OfficerAllegationFactory(officer=officer0, allegation=allegation1, final_finding='NS')
        OfficerAllegationFactory(officer=officer0, allegation=allegation2, final_finding='NS')
        OfficerAllegationFactory(officer=officer1, allegation=allegation0, final_finding='SU')
        OfficerAllegationFactory(officer=officer1, allegation=allegation1, final_finding='NS')
        OfficerAllegationFactory(officer=officer2, allegation=allegation2, final_finding='SU')
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-coaccusals', kwargs={'pk': officer0.id}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([{
            'id': officer1.id,
            'full_name': 'Officer 1',
            'allegation_count': 2,
            'sustained_count': 1,
            'complaint_percentile': 95.0,
            'race': 'White',
            'gender': 'Male',
            'birth_year': 1950,
            'coaccusal_count': 2,
            'rank': 'Police Officer',
        }, {
            'id': officer2.id,
            'full_name': 'Officer 2',
            'allegation_count': 1,
            'sustained_count': 1,
            'complaint_percentile': 99.0,
            'race': 'Black',
            'gender': 'Male',
            'birth_year': 1970,
            'coaccusal_count': 1,
            'rank': 'Police Officer',
        }])
