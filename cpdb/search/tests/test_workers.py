from datetime import datetime

import pytz
from django.test import SimpleTestCase, TestCase

from robber import expect

from data.factories import OfficerFactory, OfficerAllegationFactory, OfficerHistoryFactory, PoliceUnitFactory, \
    AllegationFactory, InvestigatorFactory, InvestigatorAllegationFactory
from search.workers import (
    ReportWorker, OfficerWorker, UnitWorker, UnitOfficerWorker,
    NeighborhoodsWorker, CommunityWorker, CRWorker, AreaWorker, TRRWorker, RankWorker,
    DateCRWorker, DateTRRWorker, ZipCodeWorker, LawsuitWorker,
    DateOfficerWorker, SearchTermItemWorker, InvestigatorCRWorker
)
from search.doc_types import (
    ReportDocType, UnitDocType, AreaDocType, CrDocType, TRRDocType, RankDocType,
    ZipCodeDocType, LawsuitDocType
)
from officers.doc_types import OfficerInfoDocType
from search.tests.utils import IndexMixin
from search_terms.factories import SearchTermItemFactory, SearchTermCategoryFactory
from trr.factories import TRRFactory


class ReportWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        doc = ReportDocType(
            publication='publication', title='title',
            author='author', excerpt='excerpt')
        doc.save()

        self.refresh_index()

        response = ReportWorker().search('author')
        expect(response.hits.total).to.be.equal(1)


class OfficerWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search_prioritizing_allegation_count(self):
        doc = OfficerInfoDocType(
            full_name='full name', badge='123', allegation_count=10)
        doc.save()
        doc = OfficerInfoDocType(
            full_name='funny naga', badge='456', allegation_count=20)
        doc.save()

        self.refresh_index()

        response = OfficerWorker().search('fu na')

        expect(response.hits.total).to.equal(2)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('funny naga')
        expect(response.hits.hits[1]['_source']['full_name']).to.eq('full name')

    def test_search_prioritizing_tags(self):
        doc = OfficerInfoDocType(
            full_name='some dude', badge='123', allegation_count=10)
        doc.save()
        doc = OfficerInfoDocType(
            full_name='another guy', badge='456', allegation_count=10, tags='somersault')
        doc.save()

        self.refresh_index()

        response = OfficerWorker().search('some')

        expect(response.hits.total).to.equal(2)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('another guy')
        expect(response.hits.hits[1]['_source']['full_name']).to.eq('some dude')

    def test_search_by_officer_id(self):
        doc = OfficerInfoDocType(full_name='some dude', badge='123', meta={'_id': '456'})
        doc.save()
        doc2 = OfficerInfoDocType(full_name='another guy', badge='789', meta={'_id': '012'})
        doc2.save()

        self.refresh_index()

        response = OfficerWorker().search('456')

        expect(response.hits.total).to.be.equal(1)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('some dude')

    def test_search_officer_badge(self):
        OfficerInfoDocType(full_name='John Doe', badge='100123').save()

        self.refresh_index()

        response = OfficerWorker().search('100')

        expect(response.hits.total).to.equal(1)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('John Doe')

    def test_prioritizing_autocomplete_and_keyword_on_badge_and_historic_badges(self):
        OfficerInfoDocType(
            full_name='Badge-Matched Guy',
            badge='00123',
            badge_keyword='00123',
        ).save()
        OfficerInfoDocType(
            full_name='Historic-Badge-Matched Guy',
            historic_badges=['00123'],
            historic_badges_keyword=['00123']
        ).save()
        OfficerInfoDocType(
            full_name='Partial Badge-Matched Guy',
            badge='100123',
            badge_keyword='100123'
        ).save()
        OfficerInfoDocType(
            full_name='Partial Historic-Badge-Matched Guy',
            historic_badges=['100123'],
            historic_badges_keyword=['100123']
        ).save()
        OfficerInfoDocType(
            full_name='Unmatched Guy',
            badge='12345',
            badge_keyword='12345'
        ).save()

        self.refresh_index()
        response = OfficerWorker().search('00123')

        expect(response.hits.total).to.equal(4)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('Badge-Matched Guy')
        expect(response.hits.hits[1]['_source']['full_name']).to.eq('Historic-Badge-Matched Guy')
        expect(response.hits.hits[2]['_source']['full_name']).to.eq('Partial Badge-Matched Guy')
        expect(response.hits.hits[3]['_source']['full_name']).to.eq('Partial Historic-Badge-Matched Guy')

    def test_search_officer_historic_badge(self):
        OfficerInfoDocType(full_name='John Doe', historic_badges=['100123', '123456']).save()

        self.refresh_index()

        response = OfficerWorker().search('100')

        expect(response.hits.total).to.equal(1)
        expect(response.hits.hits[0]['_source']['full_name']).to.eq('John Doe')

    # Note: We've found that scoring of elasticsearch is incredibly complex and could not
    # be easily replicated in unit tests. Therefore we decided to stop adding tests to this
    # particular test case and instead rely more on manual testing.


class UnitWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search_by_name(self):
        doc = UnitDocType(name='name')
        doc.save()

        self.refresh_index()

        response = UnitWorker().search('name')
        expect(response.hits.total).to.be.equal(1)

    def test_search_by_description(self):
        doc = UnitDocType(description='foo bar')
        doc.save()

        self.refresh_index()

        response = UnitWorker().search('foo')
        expect(response.hits.total).to.be.equal(1)


class NeighborhoodsWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        doc = AreaDocType(name='name', area_type='neighborhood')
        doc.save()

        self.refresh_index()

        response = NeighborhoodsWorker().search('name')
        expect(response.hits.total).to.be.equal(1)


class CommunityWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        doc = AreaDocType(name='name', area_type='community')
        doc.save()

        self.refresh_index()

        response = CommunityWorker().search('name')
        expect(response.hits.total).to.be.equal(1)


class AreaWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search_sort_by_name(self):
        doc = AreaDocType(name='name1', area_type='community')
        doc.save()
        doc = AreaDocType(name='name2')
        doc.save()

        self.refresh_index()

        response = AreaWorker().search('name')
        expect(response.hits.total).to.be.equal(2)
        expect(response[0].name).to.be.eq('name1')
        expect(response[1].name).to.be.eq('name2')

    def test_search_sort_by_allegation_count(self):
        doc1 = AreaDocType(name='name1', area_type='community', allegation_count=101)
        doc2 = AreaDocType(name='name2', area_type='community', allegation_count=201)
        doc3 = AreaDocType(name='name3', area_type='community', allegation_count=201)

        doc1.save()
        doc2.save()
        doc3.save()

        self.refresh_index()

        response = AreaWorker().search('name')
        expect(response.hits.total).to.be.equal(3)
        expect(response[0].name).to.be.eq('name2')
        expect(response[1].name).to.be.eq('name3')
        expect(response[2].name).to.be.eq('name1')


class UnitOfficerWorkerTestCase(IndexMixin, TestCase):
    def setUp(self):
        super(UnitOfficerWorkerTestCase, self).setUp()
        officer1 = OfficerFactory(first_name='Kevin', last_name='Osborn')
        officer2 = OfficerFactory(first_name='Kevin', last_name='Cascone')
        officer3 = OfficerFactory(first_name='Cristiano', last_name='Cascone')
        OfficerAllegationFactory(officer=officer1)
        unit1 = PoliceUnitFactory(unit_name='001', description='foo')
        OfficerHistoryFactory(officer=officer1, unit=unit1)
        OfficerHistoryFactory(officer=officer2, unit=unit1)
        OfficerHistoryFactory(officer=officer3, unit__unit_name='002', unit__description='bar')
        self.rebuild_index()
        self.refresh_index()

    def test_search_by_unit_name(self):
        response = UnitOfficerWorker().search('001')
        expect(response.hits.total).to.be.equal(2)
        expect(response.hits[0].full_name).to.be.eq('Kevin Osborn')
        expect(response.hits[1].full_name).to.be.eq('Kevin Cascone')

    def test_search_by_unit_description(self):
        response = UnitOfficerWorker().search('foo')
        expect(response.hits.total).to.be.equal(2)
        expect(response.hits[0].full_name).to.be.eq('Kevin Osborn')
        expect(response.hits[1].full_name).to.be.eq('Kevin Cascone')


class CRWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        CrDocType(crid='123456').save()
        CrDocType(crid='123789').save()
        CrDocType(crid='789').save()
        self.refresh_index()

        response = CRWorker().search('123')
        expect(response.hits.total).to.be.equal(2)
        expect(set([hit.crid for hit in response.hits])).to.be.eq({'123456', '123789'})

    def test_search_text_content(self):
        CrDocType(crid='123456').save()
        CrDocType(
            crid='123789',
            attachment_files=[{'id': 1, 'text_content': 'CHICAGO POLICE DEPARTMENT RD I HT334604'}]
        ).save()
        self.refresh_index()

        response = CRWorker().search('CHICAGO')
        expect(response.hits.total).to.be.equal(1)

        doc = response.hits[0]
        expect(doc.crid).to.be.eq('123789')
        expect(
            doc.meta.inner_hits.attachment_files.hits[0].meta.highlight['attachment_files.text_content'][0]
        ).to.contain('<em>CHICAGO </em>')


class DateCRWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        CrDocType(crid='123', incident_date='2007-12-27').save()
        CrDocType(crid='456', incident_date='2008-12-27').save()
        CrDocType(crid='789', incident_date='2008-12-27').save()
        self.refresh_index()

        response = DateCRWorker().search('', dates=['2008-12-27'])
        expect(response.hits.total).to.be.equal(2)
        expect(set([hit.crid for hit in response.hits])).to.be.eq({'456', '789'})


class TRRWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        TRRDocType(_id='123').save()
        TRRDocType(_id='789').save()
        self.refresh_index()

        response = TRRWorker().search('123')
        expect(response.hits.total).to.be.equal(1)
        expect(response.hits[0]._id).to.be.eq('123')


class DateTRRWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        TRRDocType(_id='123', trr_datetime='2007-12-27').save()
        TRRDocType(_id='456', trr_datetime='2008-12-27').save()
        TRRDocType(_id='789', trr_datetime='2008-12-27').save()
        self.refresh_index()

        response = DateTRRWorker().search('', dates=['2008-12-27'])
        expect(response.hits.total).to.be.equal(2)
        expect(set([hit._id for hit in response.hits])).to.be.eq({'456', '789'})


class LawsuitWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        LawsuitDocType(
            _id='1',
            case_no='00-L-5230',
            primary_cause='ILLEGAL SEARCH/SEIZURE',
            summary='Lawsuit Summary',
        ).save()
        LawsuitDocType(
            _id='2',
            case_no='00-L-5231',
            primary_cause='EXCESSIVE FORCE/SERIOUS',
            summary='Lawsuit Summary',
        ).save()
        LawsuitDocType(
            _id='3',
            case_no='18-CV-6054',
            primary_cause='FALSE ARREST',
            summary='To cover up their use of excessive force, officers falsely charged Givens with battery',
        ).save()
        LawsuitDocType(
            _id='4',
            case_no='18-CV-6055',
            primary_cause='FAILURE TO PROVIDE MEDICAL CARE',
            summary='Lawsuit Summary',
        ).save()
        self.refresh_index()

        response = LawsuitWorker().search('00-L-523')
        expect(response.hits.total).to.be.equal(2)
        expect(set([hit.case_no for hit in response.hits])).to.be.eq({'00-L-5230', '00-L-5231'})

        response = LawsuitWorker().search('EXCESSIVE')
        expect(response.hits.total).to.be.equal(2)
        expect(set([hit.case_no for hit in response.hits])).to.be.eq({'00-L-5231', '18-CV-6054'})


class RankWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search_by_rank(self):
        RankDocType(rank='Officer').save()

        self.refresh_index()

        response = RankWorker().search('Officer')
        expect(response.hits.total).to.equal(1)

    def test_search_by_tag(self):
        RankDocType(tags=['rank'], rank='Civilian', active_officers_count=1).save()
        RankDocType(tags=['rank'], rank='Detective', active_officers_count=2).save()
        RankDocType(tags=['rank'], rank='Officer', active_officers_count=3).save()

        self.refresh_index()

        response = RankWorker().search('rank')
        expect(response.hits.total).to.equal(3)
        expect([record.rank for record in response.hits]).to.eq(['Officer', 'Detective', 'Civilian'])


class ZipCodeWorkerTestCase(IndexMixin, SimpleTestCase):
    def test_search(self):
        ZipCodeDocType(zip_code='123456', tags=['zipcode']).save()
        ZipCodeDocType(zip_code='555555', tags=['zipcode']).save()

        self.refresh_index()

        response1 = ZipCodeWorker().search('123456')
        response2 = ZipCodeWorker().search('zipcode')
        expect(response1.hits.total).to.be.equal(1)
        expect(response2.hits.total).to.be.equal(2)


class DateOfficerWorkerTestCase(IndexMixin, TestCase):
    def test_search(self):
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

        response = DateOfficerWorker().search('', dates=['2004-10-10'])
        expect({record.id for record in response.hits}).to.eq({1, 2})


class SearchTermItemWorkerTestCase(IndexMixin, TestCase):
    def test_search(self):
        SearchTermItemFactory(
            slug='communities',
            name='Communities',
            category=SearchTermCategoryFactory(name='Geography'),
            description='Community description',
            call_to_action_type='view_all',
            link='http://lvh.me'
        )
        SearchTermItemFactory(
            slug='wards',
            name='Wards',
            category=SearchTermCategoryFactory(name='Geography'),
            description='Community description',
            call_to_action_type='view_all',
            link='http://lvh.me'
        )

        self.rebuild_index()
        self.refresh_index()

        response_1 = SearchTermItemWorker().search('Geography')
        response_2 = SearchTermItemWorker().search('Wards')

        expect(response_1.hits.total).to.eq(2)
        expect(response_2.hits.total).to.eq(1)
        expect({hit.name for hit in response_1.hits}).to.be.eq({'Communities', 'Wards'})
        expect({hit.name for hit in response_2.hits}).to.be.eq({'Wards'})


class InvestigatorCRWorkerTestCase(IndexMixin, TestCase):
    def test_search(self):
        allegation_1 = AllegationFactory(crid='123456')
        allegation_2 = AllegationFactory(crid='654321')
        officer = OfficerFactory(id=123, first_name='Edward', last_name='May')
        investigator_1 = InvestigatorFactory(first_name='Jerome', last_name='Finnigan')
        investigator_2 = InvestigatorFactory(officer=officer)
        InvestigatorAllegationFactory(investigator=investigator_1, allegation=allegation_1)
        InvestigatorAllegationFactory(investigator=investigator_2, allegation=allegation_2)

        self.rebuild_index()
        self.refresh_index()

        response_1 = InvestigatorCRWorker().search(term='Jerome')
        response_2 = InvestigatorCRWorker().search(term='May')

        expect(response_1.hits.total).to.eq(1)
        expect(response_1.hits[0].investigator_names).to.eq(['Jerome Finnigan'])
        expect(response_2.hits.total).to.eq(1)
        expect(response_2.hits[0].investigator_names).to.eq(['Edward May'])
