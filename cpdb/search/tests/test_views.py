from mock import patch

from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect

from data.factories import OfficerFactory, OfficerHistoryFactory, PoliceUnitFactory, AllegationFactory
from trr.factories import TRRFactory
from search.tests.utils import IndexMixin


class SearchV1ViewSetTestCase(IndexMixin, APITestCase):
    @patch('search.views.SearchManager.search')
    def test_list_with_term(self, search):
        text = 'any_text'
        search.return_value = 'anything_suggester_returns'

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': text,
            'contentType': 'OFFICER'
        })

        expect(response.status_code).to.equal(status.HTTP_200_OK)
        expect(response.data).to.equal('anything_suggester_returns')
        search.assert_called_with(text, content_type='OFFICER')

    def test_search_unit_officer(self):
        officer = OfficerFactory()
        OfficerHistoryFactory(officer=officer, unit=PoliceUnitFactory(unit_name='123'))

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': 12,
        })

        results = response.data['UNIT > OFFICERS']
        expect(results).to.have.length(1)

        expect(results[0]['name']).to.eq(officer.full_name)

    def test_search_cr_result(self):
        AllegationFactory(crid='123').save()
        AllegationFactory(crid='456').save()

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': '123',
        })

        results = response.data['CR']
        expect(results).to.have.length(1)

        expect(results[0]['crid']).to.eq('123')

    def test_search_date_cr_result(self):
        AllegationFactory(crid='123', incident_date='2007-12-27').save()
        AllegationFactory(crid='456', incident_date='2008-12-27').save()

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': '2008-12-27',
        })

        results = response.data['DATE > CR']
        expect(results).to.have.length(1)

        expect(results[0]['crid']).to.eq('456')

    def test_search_trr_result(self):
        TRRFactory(id='123456').save()
        TRRFactory(id='456789').save()

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': '123456',
        })

        results = response.data['TRR']
        expect(results).to.have.length(1)

        expect(results[0]['id']).to.eq('123456')

    def test_search_date_trr_result(self):
        TRRFactory(id='123', trr_datetime='2007-12-27').save()
        TRRFactory(id='456', trr_datetime='2008-12-27').save()

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': '2008-12-27',
        })

        results = response.data['DATE > TRR']
        expect(results).to.have.length(1)

        expect(results[0]['id']).to.eq('456')

    def test_retrieve_single_with_content_type(self):
        OfficerFactory(first_name='Kevin', last_name='Osborn', id=123)

        self.rebuild_index()
        self.refresh_index()

        text = 'Ke'
        retrieve_single_url = reverse('api:suggestion-single')
        response = self.client.get(retrieve_single_url, {
            'term': text,
            'contentType': 'OFFICER'
        })
        expect(response.status_code).to.equal(status.HTTP_200_OK)
        expect(response.data['count']).to.equal(1)
        expect(response.data['next']).to.equal(None)
        expect(response.data['previous']).to.equal(None)
        expect(len(response.data['results'])).to.eq(1)
        expect(response.data['results'][0]['id']).to.eq('123')

    def test_retrieve_single_page_size(self):
        OfficerFactory.create_batch(40, first_name='Steve')

        self.rebuild_index()
        self.refresh_index()

        retrieve_single_url = reverse('api:suggestion-single')
        response = self.client.get(retrieve_single_url, {
            'term': 'Ste',
            'contentType': 'OFFICER'
        })
        expect(response.status_code).to.equal(status.HTTP_200_OK)
        expect(response.data['count']).to.equal(40)
        expect(response.data['next']).to.ne(None)
        expect(len(response.data['results'])).to.eq(30)

    def test_retrieve_single_without_content_type(self):
        text = 'Ke'
        retrieve_single_url = reverse('api:suggestion-single')
        response = self.client.get(retrieve_single_url, {
            'term': text
        })
        expect(response.status_code).to.equal(status.HTTP_400_BAD_REQUEST)


class SearchV2ViewSetTestCase(APITestCase):
    @patch('search.views.SearchManager.search')
    def test_retrieve_ok(self, search):
        text = 'any_text'
        search.return_value = 'anything_suggester_returns'

        url = reverse('api-v2:search-list')
        response = self.client.get(url, {
            'term': text,
            'contentType': 'OFFICER'
        })

        expect(response.status_code).to.equal(status.HTTP_200_OK)
        expect(response.data).to.equal('anything_suggester_returns')
        search.assert_called_with(text, content_type='OFFICER')
