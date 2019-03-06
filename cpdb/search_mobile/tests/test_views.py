from datetime import datetime

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

import pytz
from mock import patch
from robber import expect

from data.cache_managers import allegation_cache_manager
from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, InvestigatorFactory, InvestigatorAllegationFactory
)
from trr.factories import TRRFactory
from search.tests.utils import IndexMixin


class SearchV2ViewSetTestCase(IndexMixin, APITestCase):
    @patch('search.views.SearchManager.suggest_sample')
    def test_list_ok(self, suggest_sample):
        suggest_sample.return_value = 'anything_suggester_returns'

        url = reverse('api-v2:search-mobile-list', kwargs={})
        response = self.client.get(url, {})

        expect(response.status_code).to.equal(status.HTTP_200_OK)
        expect(response.data).to.equal('anything_suggester_returns')
        suggest_sample.assert_called_with()

    def test_search_date_officers_result(self):
        officer_1 = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=2, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4)

        allegation_1 = AllegationFactory(incident_date=datetime(2004, 10, 10, tzinfo=pytz.utc))
        allegation_2 = AllegationFactory(incident_date=datetime(2009, 10, 6, tzinfo=pytz.utc))
        OfficerAllegationFactory(officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(officer=officer_3, allegation=allegation_2)

        TRRFactory(trr_datetime=datetime(2004, 10, 10, tzinfo=pytz.utc), officer=officer_2)
        TRRFactory(trr_datetime=datetime(2010, 5, 7, tzinfo=pytz.utc), officer=officer_4)

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': '2004-10-10'
        })
        results = response.data['DATE > OFFICERS']
        expect({record['id'] for record in results}).to.eq({'1', '2'})

    def test_retrieve_single_search_date_officers_result(self):
        officer_1 = OfficerFactory(id=1, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=2, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4)

        allegation_1 = AllegationFactory(incident_date=datetime(2004, 10, 10, tzinfo=pytz.utc))
        allegation_2 = AllegationFactory(incident_date=datetime(2009, 10, 6, tzinfo=pytz.utc))
        OfficerAllegationFactory(officer=officer_1, allegation=allegation_1)
        OfficerAllegationFactory(officer=officer_3, allegation=allegation_2)

        TRRFactory(trr_datetime=datetime(2004, 10, 10, tzinfo=pytz.utc), officer=officer_2)
        TRRFactory(trr_datetime=datetime(2010, 5, 7, tzinfo=pytz.utc), officer=officer_4)

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-single')
        response = self.client.get(url, {
            'term': '10-10-2004',
            'contentType': 'DATE > OFFICERS'
        })
        results = response.data['results']
        expect({record['id'] for record in results}).to.eq({'1', '2'})

    def test_search_investigator_cr_results(self):
        allegation_1 = AllegationFactory(crid='123456', incident_date=datetime(2002, 2, 3, tzinfo=pytz.utc))
        allegation_2 = AllegationFactory(crid='654321', incident_date=datetime(2005, 2, 3, tzinfo=pytz.utc))
        officer = OfficerFactory(id=123, first_name='Edward', last_name='May')
        investigator_1 = InvestigatorFactory(first_name='Jerome', last_name='Finnigan')
        investigator_2 = InvestigatorFactory(officer=officer)
        InvestigatorAllegationFactory(investigator=investigator_1, allegation=allegation_1)
        InvestigatorAllegationFactory(investigator=investigator_2, allegation=allegation_1)
        InvestigatorAllegationFactory(investigator=investigator_1, allegation=allegation_2)
        OfficerAllegationFactory(allegation=allegation_1, allegation_category__category='Illegal Search')
        OfficerAllegationFactory(allegation=allegation_2, allegation_category__category='')

        allegation_cache_manager.cache_data()
        self.rebuild_index()
        self.refresh_index()

        url = reverse('api-v2:search-mobile-list')
        response = self.client.get(url, {
            'term': 'Jerome',
        })

        results = response.data['INVESTIGATOR > CR']
        expect(results).to.have.length(2)

        expected_results = {
            '123456': {
                'id': '123456',
                'crid': '123456',
                'category': 'Illegal Search',
                'incident_date': '2002-02-03'
            },
            '654321': {
                'id': '654321',
                'crid': '654321',
                'category': 'Unknown',
                'incident_date': '2005-02-03'
            }
        }

        for cr_data in results:
            expect(cr_data).to.eq(expected_results[cr_data['id']])
