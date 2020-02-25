from datetime import datetime, date

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from mock import patch
from robber import expect
import pytz

from data.factories import (
    OfficerFactory,
    OfficerHistoryFactory,
    PoliceUnitFactory,
    AllegationFactory,
    InvestigatorFactory,
    InvestigatorAllegationFactory,
    OfficerAllegationFactory,
    AttachmentFileFactory,
    AllegationCategoryFactory)
from search_terms.factories import SearchTermItemFactory, SearchTermCategoryFactory
from trr.factories import TRRFactory, ActionResponseFactory
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

    def test_search_cr_by_attachment_text_content(self):
        allegation_123 = AllegationFactory(crid='123')
        AllegationFactory(crid='456')
        AttachmentFileFactory(
            allegation=allegation_123,
            show=True,
            text_content='the officer pointed a gun at the victim'
        )

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': 'gun',
        })

        results = response.data['CR']
        expect(results).to.have.length(1)

        expect(results[0]['crid']).to.eq('123')
        expect(results[0]['highlight']['text_content'][0]).to.contain('a <em>gun</em> at')

    def test_search_date_cr_result(self):
        AllegationFactory(crid='123', incident_date=datetime(2007, 12, 27, tzinfo=pytz.utc)).save()
        AllegationFactory(crid='456', incident_date=datetime(2008, 12, 27, tzinfo=pytz.utc)).save()

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
        officer = OfficerFactory(
            id=123456,
            rank='Sergeant of Police',
            first_name='Jesse',
            last_name='Pinkman',
            complaint_percentile=0.0,
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
            allegation_count=1,
            resignation_date=date(2015, 4, 14)
        )
        TRRFactory(
            id='123',
            trr_datetime=datetime(2007, 12, 27, tzinfo=pytz.utc),
        )
        TRRFactory(
            id='456',
            trr_datetime=datetime(2008, 12, 27, tzinfo=pytz.utc),
            block='3000',
            street='Michigan Ave',
            taser=False,
            firearm_used=True,
            officer=officer
        )

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': '2008-12-27',
        })

        results = response.data['DATE > TRR']
        expect(results).to.have.length(1)
        expect(results[0]['id']).to.eq('456')
        expect(results[0]).to.eq({
            'id': '456',
            'trr_datetime': '2008-12-27',
            'to': '/trr/456/',
            'category': 'Firearm',
            'address': '3000 Michigan Ave',
            'officer': {
                'id': 123456,
                'full_name': 'Jesse Pinkman',
                'percentile':
                {
                    'id': 123456,
                    'percentile_trr': '3.3000',
                    'percentile_allegation_civilian': '1.1000',
                    'percentile_allegation_internal': '2.2000'
                },
                'allegation_count': 1
            }
        })

    def test_search_date_trr_result_empty_block(self):
        TRRFactory(
            id='456',
            trr_datetime=datetime(2008, 12, 27, tzinfo=pytz.utc),
            street='Michigan Ave'
        )

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': '2008-12-27',
        })

        results = response.data['DATE > TRR']
        expect(results).to.have.length(1)
        expect(results[0]['address']).to.eq('Michigan Ave')

    def test_search_date_trr_result_empty_street(self):
        TRRFactory(
            id='456',
            trr_datetime=datetime(2008, 12, 27, tzinfo=pytz.utc),
            block='3000'
        )

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': '2008-12-27',
        })

        results = response.data['DATE > TRR']
        expect(results).to.have.length(1)
        expect(results[0]['address']).to.eq('3000')

    def test_search_date_trr_result_empty_officer(self):
        TRRFactory(
            id='456',
            trr_datetime=datetime(2008, 12, 27, tzinfo=pytz.utc),
            block='3000',
            officer=None,
        )

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': '2008-12-27',
        })

        results = response.data['DATE > TRR']
        expect(results).to.have.length(1)
        expect(results[0]).not_to.contain('officer')

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

    def test_retrieve_single_cr_with_highlight(self):
        AllegationFactory(
            crid=123,
            incident_date=datetime(2007, 12, 27, tzinfo=pytz.utc),
            summary='the officer pointed a gun at the victim'
        )
        AllegationFactory(
            crid=456,
            incident_date=datetime(2000, 12, 27, tzinfo=pytz.utc),
            summary='the officer pointed a knife at the victim'
        )

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-single')
        response = self.client.get(url, {
            'term': 'gun',
            'contentType': 'CR',
        })

        expect(response.data['count']).to.eq(1)
        expect(response.data['results'][0]).to.eq({
            'id': '123',
            'crid': '123',
            'to': '/complaint/123/',
            'incident_date': '2007-12-27',
            'highlight': {
                'summary': ['the officer pointed a <em>gun</em> at the victim']
            },
            'category': 'Unknown',
            'sub_category': 'Unknown',
            'address': '',
            'victims': [],
            'coaccused': []
        })

    def test_retrieve_list_cr_with_highlight(self):
        AllegationFactory(
            crid=123,
            incident_date=datetime(2007, 12, 27, tzinfo=pytz.utc),
            summary='the officer pointed a gun at the victim'
        )
        AllegationFactory(
            crid=456,
            incident_date=datetime(2000, 12, 27, tzinfo=pytz.utc),
            summary='the officer pointed a knife at the victim'
        )

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': 'gun',
        })

        results = response.data['CR']
        expect(results).to.have.length(1)
        expect(results[0]).to.eq({
            'id': '123',
            'crid': '123',
            'to': '/complaint/123/',
            'incident_date': '2007-12-27',
            'highlight': {
                'summary': ['the officer pointed a <em>gun</em> at the victim']
            },
            'category': 'Unknown',
            'sub_category': 'Unknown',
            'address': '',
            'victims': [],
            'coaccused': []
        })

    def test_search_terms_results(self):
        SearchTermItemFactory(
            slug='communities',
            name='Communities',
            category=SearchTermCategoryFactory(name='Geography'),
            description='Community description',
            call_to_action_type='view_all',
            link='/url-mediator/session-builder/?community=123456'
        )
        SearchTermItemFactory(
            slug='wards',
            name='Wards',
            category=SearchTermCategoryFactory(name='Geography'),
            description='Ward description',
            call_to_action_type='view_all',
            link='/url-mediator/session-builder/?community=654321'
        )

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': 'Geography',
        })

        results = response.data['SEARCH-TERMS']
        expect(results).to.have.length(2)

        expect(results[0]['id']).to.eq('communities')
        expect(results[0]['name']).to.eq('Communities')
        expect(results[0]['category_name']).to.eq('Geography')
        expect(results[0]['description']).to.eq('Community description')
        expect(results[0]['call_to_action_type']).to.eq('view_all')
        expect(results[0]['link']).to.eq('http://cpdb.lvh.me/url-mediator/session-builder/?community=123456')

    def test_search_investigator_cr_results(self):
        allegation_1 = AllegationFactory(crid='123456', incident_date=datetime(2002, 2, 3, tzinfo=pytz.utc))
        allegation_2 = AllegationFactory(crid='654321', incident_date=datetime(2005, 2, 3, tzinfo=pytz.utc))
        officer = OfficerFactory(id=123, first_name='Edward', last_name='May')
        investigator_1 = InvestigatorFactory(first_name='Jerome', last_name='Finnigan')
        investigator_2 = InvestigatorFactory(officer=officer)
        InvestigatorAllegationFactory(investigator=investigator_1, allegation=allegation_1)
        InvestigatorAllegationFactory(investigator=investigator_2, allegation=allegation_1)
        InvestigatorAllegationFactory(investigator=investigator_1, allegation=allegation_2)

        self.rebuild_index()
        self.refresh_index()

        url = reverse('api:suggestion-list')
        response = self.client.get(url, {
            'term': 'Jerome',
        })

        results = response.data['INVESTIGATOR > CR']
        expect(results).to.have.length(2)

        expected_results = {
            '123456': {
                'id': '123456',
                'crid': '123456',
                'to': '/complaint/123456/',
                'incident_date': '2002-02-03',
                'category': 'Unknown',
                'sub_category': 'Unknown',
                'address': '',
                'victims': [],
                'coaccused': []
            },
            '654321': {
                'id': '654321',
                'crid': '654321',
                'to': '/complaint/654321/',
                'incident_date': '2005-02-03',
                'category': 'Unknown',
                'sub_category': 'Unknown',
                'address': '',
                'victims': [],
                'coaccused': []
            }
        }

        for cr_data in results:
            expect(cr_data).to.eq(expected_results[cr_data['id']])

    def test_retrieve_recent_search_items(self):
        OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            current_badge='123456',
            allegation_count=20,
            sustained_count=5,
            birth_year=1980,
            race='White',
            gender='M',
            rank='Police Officer'
        )
        allegation_category = AllegationCategoryFactory(category='Use of Force')
        AllegationFactory(
            crid='C12345',
            incident_date=datetime(2007, 1, 1, tzinfo=pytz.utc),
            most_common_category=allegation_category,
        )
        trr = TRRFactory(id=123, trr_datetime=datetime(2007, 1, 1, tzinfo=pytz.utc))
        ActionResponseFactory(trr=trr, force_type='Physical Force - Stunning', action_sub_category='4')
        ActionResponseFactory(trr=trr, force_type='Taser', action_sub_category='5.1')
        ActionResponseFactory(trr=trr, force_type='Impact Weapon', action_sub_category='5.2')
        ActionResponseFactory(trr=trr, force_type='Taser Display', action_sub_category='3')

        url = reverse('api:suggestion-recent-search-items')
        response = self.client.get(url, {
            'officer_ids[]': 8562,
            'crids[]': 'C12345',
            'trr_ids[]': 123,
        })

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq([
            {
                'id': 8562,
                'name': 'Jerome Finnigan',
                'race': 'White',
                'gender': 'Male',
                'rank': 'Police Officer',
                'allegation_count': 20,
                'sustained_count': 5,
                'birth_year': 1980,
                'type': 'OFFICER',
            },
            {
                'id': 'C12345',
                'crid': 'C12345',
                'category': 'Use of Force',
                'incident_date': '2007-01-01',
                'type': 'CR',
            },
            {
                'id': 123,
                'trr_datetime': '2007-01-01',
                'force_type': 'Impact Weapon',
                'type': 'TRR',
            }
        ])


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
