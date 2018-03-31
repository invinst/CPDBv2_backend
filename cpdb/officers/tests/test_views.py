import pytz
from datetime import date, datetime

from django.core.urlresolvers import reverse

from mock import patch, Mock
from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect

from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, PoliceUnitFactory,
    AllegationCategoryFactory, OfficerHistoryFactory, OfficerBadgeNumberFactory, AwardFactory
)
from trr.factories import TRRFactory
from .mixins import OfficerSummaryTestCaseMixin
from data.constants import ACTIVE_YES_CHOICE


class OfficersViewSetTestCase(OfficerSummaryTestCaseMixin, APITestCase):
    def test_summary(self):
        officer = OfficerFactory(
            first_name='Kevin', last_name='Kerl', id=123, race='White', gender='M',
            appointed_date=date(2017, 2, 27), rank='PO', resignation_date=date(2017, 12, 27),
            active=ACTIVE_YES_CHOICE, birth_year=1910
        )
        allegation = AllegationFactory()
        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerHistoryFactory(officer=officer, unit=PoliceUnitFactory(unit_name='CAND'))
        OfficerBadgeNumberFactory(officer=officer, star='123456', current=True)
        OfficerAllegationFactory(
            officer=officer, allegation=allegation, allegation_category=allegation_category, final_finding='SU',
            start_date=date(2000, 1, 1)
        )
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-summary', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 123,
            'unit': 'CAND',
            'date_of_appt': '2017-02-27',
            'date_of_resignation': '2017-12-27',
            'active': 'Active',
            'rank': 'PO',
            'full_name': 'Kevin Kerl',
            'race': 'White',
            'badge': '123456',
            'gender': 'Male',
            'birth_year': 1910,
        })

    def test_summary_no_match(self):
        response = self.client.get(reverse('api-v2:officers-summary', kwargs={'pk': 456}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def create_officer_allegation(self, officer, final_finding, final_outcome):
        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerAllegationFactory(
            officer=officer, allegation_category=allegation_category,
            final_finding=final_finding, final_outcome=final_outcome
        )

    def test_metrics(self):
        officer = OfficerFactory(id=123, complaint_percentile=90.0)
        self.create_officer_allegation(officer=officer, final_finding='NS', final_outcome='027')
        self.create_officer_allegation(officer=officer, final_finding='NS', final_outcome='028')
        self.create_officer_allegation(officer=officer, final_finding='SU', final_outcome='600')

        AwardFactory(officer=officer, award_type='Other')
        AwardFactory(officer=officer, award_type='Complimentary Letter')
        AwardFactory(officer=officer, award_type='Complimentary Letter')
        AwardFactory(officer=officer, award_type='Honorable Mention')
        AwardFactory(officer=officer, award_type='ABC Honorable Mention')

        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-metrics', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 123,
            'allegation_count': 3,
            'complaint_percentile': 90.0,
            'honorable_mention_count': 2,
            'sustained_count': 1,
            'discipline_count': 2,
            'civilian_compliment_count': 2
        })

    def test_metrics_no_match(self):
        response = self.client.get(reverse('api-v2:officers-metrics', kwargs={'pk': 456}))
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
        allegation = AllegationFactory(crid='123456')
        OfficerAllegationFactory(
            final_finding='UN', final_outcome='',
            officer=officer, start_date=date(2011, 8, 23), allegation=allegation,
            allegation_category=AllegationCategoryFactory(category='category', allegation_name='sub category')
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)

        allegation2 = AllegationFactory(crid='654321')
        OfficerAllegationFactory(
            final_finding='UN', final_outcome='009',
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

    @patch('officers.views.OfficerMetricsWorker.search')
    @patch('officers.views.OfficerPercentileWorker.get_top_officers')
    def test_top_officers_by_allegation(self, get_top_officers_mock, search_mock):
        get_top_officers_mock.return_value = [
            Mock(
                officer_id=1,
                year=2016,
                percentile_trr=0.000,
                percentile_allegation=99.995,
                percentile_allegation_civilian=99.990,
                percentile_allegation_internal=99.802,
            ),
            Mock(
                officer_id=2,
                year=2016,
                percentile_trr=0.000,
                percentile_allegation=99.993,
                percentile_allegation_civilian=99.901,
                percentile_allegation_internal=99.812,
            ),
        ]
        OfficerFactory(id=1, first_name='Clarence', last_name='Featherwater', gender='M', birth_year=1970)
        OfficerFactory(id=2, first_name='Ronald', last_name='Watts', gender='M', birth_year=1970)
        metric1 = Mock(id=1)
        metric1.to_dict.return_value = {
            'id': 1,
            'sustained_count': 20,
            'allegation_count': 10,
        }
        metric2 = Mock(id=2)
        metric2.to_dict.return_value = {
            'id': 2,
            'sustained_count': 15,
            'allegation_count': 17,
        }
        search_mock.return_value = Mock(
            hits=[metric1, metric2],
        )

        response = self.client.get(reverse('api-v2:officers-top-by-allegation'))
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq([
            {
                'id': 1,
                'full_name': 'Clarence Featherwater',
                'sustained_count': 20,
                'complaint_count': 10,
                'birth_year': 1970,
                'race': 'White',
                'gender': 'Male',
                'percentile': {
                    'officer_id': 1,
                    'year': 2016,
                    'percentile_trr': '0.000',
                    'percentile_allegation': '99.995',
                    'percentile_allegation_civilian': '99.990',
                    'percentile_allegation_internal': '99.802',
                }
            }, {
                'id': 2,
                'full_name': 'Ronald Watts',
                'sustained_count': 15,
                'complaint_count': 17,
                'race': 'White',
                'gender': 'Male',
                'birth_year': 1970,
                'percentile': {
                    'officer_id': 2,
                    'year': 2016,
                    'percentile_trr': '0.000',
                    'percentile_allegation': '99.993',
                    'percentile_allegation_civilian': '99.901',
                    'percentile_allegation_internal': '99.812',
                }
            }])

    def test_officer_percentile(self):
        appointed_date = date(2003, 1, 1)
        officer = OfficerFactory(id=1, first_name='Clarence', last_name='Featherwater',
                                 complaint_percentile=100.0, gender='M', birth_year=1970,
                                 appointed_date=appointed_date)
        OfficerFactory(id=2, first_name='Raymond', last_name='Piwnicki', complaint_percentile=50.0,
                       appointed_date=appointed_date)
        OfficerFactory(id=3, first_name='Ronald', last_name='Watts',
                       complaint_percentile=99.2, gender='M', birth_year=1960,
                       appointed_date=appointed_date)

        OfficerAllegationFactory.create_batch(
            2, officer=officer, start_date=date(2015, 1, 12),
            allegation__incident_date=datetime(2014, 1, 1),
            allegation__is_officer_complaint=False,
            final_finding='NS'
        )
        OfficerAllegationFactory.create_batch(
            2, officer=officer, start_date=date(2016, 1, 12),
            allegation__incident_date=datetime(2016, 1, 1),
            allegation__is_officer_complaint=False,
            final_finding='NS'
        )

        self.refresh_index()
        response = self.client.get(reverse('api-v2:officers-percentile', kwargs={'pk': 1}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([{
            'officer_id': 1,
            'year': 2015,
            'percentile_trr': '0.000',
            'percentile_allegation': '66.667',
            'percentile_allegation_civilian': '66.667',
            'percentile_allegation_internal': '0.000'
        }, {
            'officer_id': 1,
            'year': 2016,
            'percentile_trr': '0.000',
            'percentile_allegation': '66.667',
            'percentile_allegation_civilian': '66.667',
            'percentile_allegation_internal': '0.000'
        }])
