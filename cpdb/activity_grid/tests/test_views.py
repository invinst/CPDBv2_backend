from datetime import datetime, date

import pytz
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from robber import expect

from activity_grid.factories import ActivityCardFactory, ActivityPairCardFactory
from activity_grid.models import ActivityPairCard
from data.cache_managers import cache_all
from data.factories import OfficerFactory, OfficerAllegationFactory, AllegationFactory
from data.models import Officer


class ActivityGridViewSetTestCase(APITestCase):
    def test_list_return_exactly_80_items(self):
        ActivityCardFactory.create_batch(50)
        ActivityPairCardFactory.create_batch(50)

        response = self.client.get(reverse('api-v2:activity-grid-list'))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.have.length(80)

    def test_list_item_content(self):
        officer1 = OfficerFactory(
            first_name='Jerome',
            last_name='Finnigan',
            birth_year=1950,
            race='Asian',
            gender='M',
            appointed_date=datetime(2011, 1, 1, tzinfo=pytz.utc),
            complaint_percentile=50.0,
            allegation_count=6,
            sustained_count=2,
            rank='Police Officer',
        )
        officer2 = OfficerFactory(
            first_name='Raymond',
            last_name='Piwinicki',
            birth_year=1960,
            race='White',
            gender='M',
            appointed_date=datetime(2012, 1, 1, tzinfo=pytz.utc),
            complaint_percentile=0.0,
            allegation_count=1,
            sustained_count=1,
            rank='Police Officer',
        )
        allegation = AllegationFactory(incident_date=datetime(2014, 1, 1, tzinfo=pytz.utc))
        OfficerAllegationFactory(
            officer=officer1,
            allegation=allegation,
            final_finding='SU',
            start_date=date(2014, 1, 1),
        )
        OfficerAllegationFactory(
            officer=officer2,
            allegation=allegation,
            final_finding='SU',
            start_date=date(2014, 1, 1),
        )
        OfficerAllegationFactory(
            officer=officer1,
            final_finding='SU',
            allegation__incident_date=datetime(2016, 1, 1, tzinfo=pytz.utc),
            start_date=date(2016, 1, 1)
        )
        OfficerAllegationFactory.create_batch(
            4,
            officer=officer1,
            final_finding='NS',
            start_date=date(2015, 1, 1),
            allegation__incident_date=datetime(2015, 2, 20, tzinfo=pytz.utc)
        )
        ActivityCardFactory(officer=officer1, last_activity=datetime(2018, 12, 22, tzinfo=pytz.utc))
        ActivityCardFactory(officer=officer2, last_activity=datetime(2018, 10, 15, tzinfo=pytz.utc))
        ActivityPairCardFactory(
            officer1=officer1, officer2=officer2, last_activity=datetime(2018, 5, 20, tzinfo=pytz.utc)
        )

        cache_all()

        url = reverse('api-v2:activity-grid-list')
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([{
            'id': officer1.id,
            'full_name': 'Jerome Finnigan',
            'complaint_count': 6,
            'sustained_count': 2,
            'birth_year': 1950,
            'race': 'Asian',
            'gender': 'Male',
            'rank': 'Police Officer',
            'percentile_trr': '0.0000',
            'percentile_allegation_internal': '0.0000',
            'percentile_allegation_civilian': '50.0000',
            'percentile_allegation': '50.0000',
            'kind': 'single_officer',
        }, {
            'id': officer2.id,
            'full_name': 'Raymond Piwinicki',
            'complaint_count': 1,
            'sustained_count': 1,
            'birth_year': 1960,
            'race': 'White',
            'gender': 'Male',
            'rank': 'Police Officer',
            'percentile_trr': '0.0000',
            'percentile_allegation_internal': '0.0000',
            'percentile_allegation_civilian': '0.0000',
            'percentile_allegation': '0.0000',
            'kind': 'single_officer',
        }, {
            'officer1': {
                'id': officer1.id,
                'full_name': 'Jerome Finnigan',
                'birth_year': 1950,
                'race': 'Asian',
                'gender': 'Male',
                'rank': 'Police Officer',
                'percentile_trr': '0.0000',
                'percentile_allegation_internal': '0.0000',
                'percentile_allegation_civilian': '50.0000',
                'percentile_allegation': '50.0000',
                'complaint_count': 6,
                'sustained_count': 2,
            },
            'officer2': {
                'id': officer2.id,
                'full_name': 'Raymond Piwinicki',
                'birth_year': 1960,
                'race': 'White',
                'gender': 'Male',
                'rank': 'Police Officer',
                'percentile_trr': '0.0000',
                'percentile_allegation_internal': '0.0000',
                'percentile_allegation_civilian': '0.0000',
                'percentile_allegation': '0.0000',
                'complaint_count': 1,
                'sustained_count': 1,
            },
            'coaccusal_count': 1,
            'kind': 'coaccused_pair',
        }])

    def test_list_order(self):
        ActivityCardFactory.create_batch(3, important=True)
        ActivityCardFactory.create_batch(10, last_activity=datetime(2017, 5, 21, tzinfo=pytz.utc))
        ActivityCardFactory.create_batch(10)
        ActivityCardFactory.create_batch(17, last_activity=datetime(2017, 7, 21, tzinfo=pytz.utc))
        ActivityPairCardFactory.create_batch(3, important=True)
        ActivityPairCardFactory.create_batch(10, last_activity=datetime(2017, 5, 20, tzinfo=pytz.utc))
        ActivityPairCardFactory.create_batch(10)
        ActivityPairCardFactory.create_batch(17, last_activity=datetime(2017, 7, 20, tzinfo=pytz.utc))
        url = reverse('api-v2:activity-grid-list')

        cache_all()
        response = self.client.get(url)

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.have.length(80)

        for item in response.data[:3]:
            activity_card = Officer.objects.get(pk=item['id']).activity_card
            expect(activity_card.important).to.be.true()

        for item in response.data[3:6]:
            pair_card = ActivityPairCard.objects.get(
                officer1_id=item['officer1']['id'], officer2_id=item['officer2']['id']
            )
            expect(pair_card.important).to.be.true()

        for item in response.data[6:23]:
            activity_card = Officer.objects.get(pk=item['id']).activity_card
            expect(activity_card.last_activity).to.eq(datetime(2017, 7, 21, tzinfo=pytz.utc))

        for item in response.data[23:40]:
            pair_card = ActivityPairCard.objects.get(
                officer1_id=item['officer1']['id'], officer2_id=item['officer2']['id']
            )
            expect(pair_card.last_activity).to.eq(datetime(2017, 7, 20, tzinfo=pytz.utc))

        for item in response.data[40:50]:
            activity_card = Officer.objects.get(pk=item['id']).activity_card
            expect(activity_card.last_activity).to.eq(datetime(2017, 5, 21, tzinfo=pytz.utc))

        for item in response.data[50:60]:
            pair_card = ActivityPairCard.objects.get(
                officer1_id=item['officer1']['id'], officer2_id=item['officer2']['id']
            )
            expect(pair_card.last_activity).to.eq(datetime(2017, 5, 20, tzinfo=pytz.utc))
