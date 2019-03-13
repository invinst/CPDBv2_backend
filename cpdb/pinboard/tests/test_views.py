from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect

from pinboard.models import Pinboard
from data.factories import OfficerFactory, AllegationFactory
from pinboard.factories import PinboardFactory


class PinboardAPITestCase(APITestCase):
    def test_retrieve_pinboard(self):
        officer1 = OfficerFactory(id=1)
        officer2 = OfficerFactory(id=2)

        allegation1 = AllegationFactory(crid='123abc')

        PinboardFactory.create(
            id=1,
            title='My Pinboard',
            officers=(officer1, officer2),
            allegations=(allegation1,),
            description='abc',
        )

        response = self.client.get(reverse('api-v2:pinboards-detail', kwargs={'pk': '1'}))

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 1,
            'title': 'My Pinboard',
            'officer_ids': [1, 2],
            'crids': ['123abc'],
            'description': 'abc',
        })

    def test_update_pinboard_in_the_same_session(self):
        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')
        AllegationFactory(crid='456def')

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            {
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'description': 'abc',
            }
        )
        pinboard_id = response.data['id']

        response = self.client.put(
            reverse('api-v2:pinboards-detail', kwargs={'pk': pinboard_id}),
            {
                'title': 'New Pinboard',
                'officer_ids': [1],
                'crids': ['456def'],
                'description': 'def',
            }
        )

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': pinboard_id,
            'title': 'New Pinboard',
            'officer_ids': [1],
            'crids': ['456def'],
            'description': 'def',
        })

        pinboard = Pinboard.objects.get(id=pinboard_id)
        officer_ids = set([officer.id for officer in pinboard.officers.all()])
        crids = set([allegation.crid for allegation in pinboard.allegations.all()])

        expect(pinboard.title).to.eq('New Pinboard')
        expect(pinboard.description).to.eq('def')
        expect(officer_ids).to.eq({1})
        expect(crids).to.eq({'456def'})

    def test_update_pinboard_out_of_session(self):
        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')
        AllegationFactory(crid='456def')

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            {
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'description': 'abc',
            }
        )
        self.client.cookies.clear()

        response = self.client.put(
            reverse('api-v2:pinboards-detail', kwargs={'pk': response.data['id']}),
            {
                'title': 'New Pinboard',
                'officer_ids': [1],
                'crids': ['456def'],
                'description': 'def',
            },
        )

        expect(response.status_code).to.eq(status.HTTP_403_FORBIDDEN)

    def test_create_pinboard(self):
        OfficerFactory(id=1)
        OfficerFactory(id=2)

        AllegationFactory(crid='123abc')

        response = self.client.post(
            reverse('api-v2:pinboards-list'),
            {
                'title': 'My Pinboard',
                'officer_ids': [1, 2],
                'crids': ['123abc'],
                'description': 'abc',
            }
        )

        expect(response.status_code).to.eq(status.HTTP_201_CREATED)
        expect(response.data).to.eq({
            'id': 1,
            'title': 'My Pinboard',
            'officer_ids': [1, 2],
            'crids': ['123abc'],
            'description': 'abc'
        })

        expect(Pinboard.objects.count()).to.eq(1)
        pinboard = Pinboard.objects.all()

        expect(pinboard[0].title).to.eq('My Pinboard')
        expect(pinboard[0].description).to.eq('abc')
        expect(set(pinboard.values_list('officers', flat=True))).to.eq({1, 2})
        expect(set(pinboard.values_list('allegations', flat=True))).to.eq({'123abc'})
