from mock import Mock, patch
from datetime import datetime
from decimal import Decimal

from django.test import SimpleTestCase, TestCase

from robber import expect
import pytz

from data.cache_managers import allegation_cache_manager
from data.constants import ACTIVE_YES_CHOICE
from search.search_indexers import (
    CrIndexer, TRRIndexer, BaseIndexer, UnitIndexer, AreaIndexer, IndexerManager, RankIndexer, SearchTermItemIndexer
)
from data.factories import (
    AreaFactory, OfficerFactory, PoliceUnitFactory,
    OfficerHistoryFactory, AllegationFactory,
    OfficerAllegationFactory, RacePopulationFactory,
    SalaryFactory, AllegationCategoryFactory,
    InvestigatorAllegationFactory, InvestigatorFactory,
    VictimFactory, AttachmentFileFactory
)
from search_terms.factories import SearchTermItemFactory, SearchTermCategoryFactory
from trr.factories import TRRFactory, ActionResponseFactory
from shared.tests.utils import create_object


def mock_object(**kwargs):
    class MyObject(object):
        pass

    obj = MyObject()
    for key, val in kwargs.items():
        setattr(obj, key, val)
    return obj


class BaseIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        expect(lambda: BaseIndexer().get_queryset()).to.throw(NotImplementedError)

    def test_extract_datum(self):
        expect(lambda: BaseIndexer().extract_datum('anything')).to.throw(NotImplementedError)

    def test_extract_datum_with_id_datum_dict(self):
        datum = Mock(pk='11')
        indexer = BaseIndexer()
        indexer.extract_datum = Mock(return_value={'foo': 'bar'})
        expect(indexer.extract_datum_with_id(datum)).to.eq({
            'foo': 'bar',
            'meta': {
                'id': '11'
            }
        })

    def test_extract_datum_with_no_id_datum_dict(self):
        datum = create_object({'foo': 'bar'})
        indexer = BaseIndexer()
        indexer.extract_datum = lambda a: {'foo': a.foo}
        expect(indexer.extract_datum_with_id(datum)).to.eq({'foo': 'bar'})

    def test_extract_datum_with_id_datum_list(self):
        datum = Mock(pk='11')
        indexer = BaseIndexer()
        indexer.extract_datum = Mock(return_value=[{'foo': 'bar'}])
        expect(indexer.extract_datum_with_id(datum)).to.eq([{'foo': 'bar'}])

    def test_docs_from_data_list(self):
        indexer = BaseIndexer()
        indexer.doc_type_klass = Mock()
        indexer.get_queryset = Mock(return_value=['something'])
        indexer.extract_datum_with_id = Mock(return_value=[{'abc': 'def'}])
        indexer._prepare_doc = lambda o: o
        expect(list(indexer.docs())).to.eq([{'abc': 'def'}])

    def test_docs_from_data_dict(self):
        indexer = BaseIndexer()
        indexer.doc_type_klass = Mock()
        indexer.get_queryset = Mock(return_value=['something'])
        indexer.extract_datum_with_id = Mock(return_value={'abc': 'def'})
        indexer._prepare_doc = lambda o: o
        expect(list(indexer.docs())).to.eq([{'abc': 'def'}])


class UnitIndexerTestCase(TestCase):
    def test_get_queryset(self):
        expect(UnitIndexer().get_queryset().count()).to.eq(0)
        PoliceUnitFactory()
        expect(UnitIndexer().get_queryset().count()).to.eq(1)

    def test_extract_datum(self):
        datum = PoliceUnitFactory(unit_name='011', description='description')
        officer = OfficerFactory()
        officer2 = OfficerFactory()
        OfficerHistoryFactory(officer=officer, unit=datum, end_date=None)
        OfficerHistoryFactory(officer=officer2, unit=datum)

        expect(
            UnitIndexer().extract_datum(datum)
        ).to.be.eq({
            'name': '011',
            'description': 'description',
            'url': datum.v1_url,
            'to': datum.v2_to,
            'active_member_count': 1,
            'member_count': 2,
            'long_name': 'Unit 011',
        })


class AreaIndexerTestCase(TestCase):
    def test_get_queryset(self):
        area_indexer = AreaIndexer()
        expect(area_indexer.get_queryset().count()).to.eq(0)
        AreaFactory()
        expect(area_indexer.get_queryset().count()).to.eq(1)
        expect(area_indexer._percentiles).to.have.length(0)

    def test_get_queryset_with_police_district(self):
        area1 = AreaFactory(area_type='police-districts')
        RacePopulationFactory(race='White', count=1000, area=area1)
        AllegationFactory.create_batch(2, areas=[area1])

        area2 = AreaFactory(area_type='police-districts')
        RacePopulationFactory(race='Black', count=100, area=area2)
        AllegationFactory(areas=[area2])

        area3 = AreaFactory(area_type='community')
        RacePopulationFactory(race='Black', count=10, area=area3)
        AllegationFactory.create_batch(3, areas=[area3])

        area_indexer = AreaIndexer()
        expect(area_indexer.get_queryset().count()).to.eq(3)
        expect(area_indexer._percentiles).to.eq({
            area1.id: 0.0,
            area2.id: 50.0
        })

    def test_extract_datum(self):
        commander = OfficerFactory(first_name='Captain', last_name='America')
        area = AreaFactory(
            name='name',
            tags=['tag'],
            median_income=343,
            area_type='police-districts',
            commander=commander,
            description='Other Name'
        )
        RacePopulationFactory(
            area=area,
            race='Asian',
            count=101
        )
        area_indexer = AreaIndexer()
        area_indexer._percentiles = {area.id: 0}

        expect(
            area_indexer.extract_datum(area)
        ).to.be.eq({
            'name': 'Other Name',
            'url': area.v1_url,
            'area_type': 'police-district',
            'tags': ['tag', 'police district'],
            'allegation_count': 0,
            'officers_most_complaint': [],
            'most_common_complaint': [],
            'race_count': [{
                'race': 'Asian',
                'count': 101
            }],
            'allegation_percentile': 0,
            'median_income': 343,
            'commander': {
                'id': commander.id,
                'full_name': 'Captain America',
                'allegation_count': 0,
            },
            'alderman': None,
            'police_hq': None
        })

    def test_extract_datum_with_police_hq(self):
        police_district_area = AreaFactory(area_type='police_district', name='22nd')
        beat_area = AreaFactory(
            name='1',
            tags=['tag'],
            median_income=343,
            area_type='beat',
            police_hq=police_district_area)
        expect(
            AreaIndexer().extract_datum(beat_area)
        ).to.be.eq({
            'name': '1',
            'url': beat_area.v1_url,
            'area_type': 'beat',
            'tags': ['tag', 'beat'],
            'allegation_count': 0,
            'officers_most_complaint': [],
            'most_common_complaint': [],
            'race_count': [],
            'allegation_percentile': None,
            'median_income': 343,
            'commander': None,
            'alderman': None,
            'police_hq': '22nd'
        })

    def test_extract_datum_with_ward_name(self):
        area = AreaFactory(
            name='name',
            tags=['tag'],
            median_income=343,
            area_type='wards',
            alderman='IronMan',
            description='Other Name'
        )
        RacePopulationFactory(
            area=area,
            race='Asian',
            count=101
        )

        expect(
            AreaIndexer().extract_datum(area)
        ).to.be.eq({
            'name': 'name',
            'url': area.v1_url,
            'area_type': 'ward',
            'tags': ['tag', 'ward'],
            'allegation_count': 0,
            'officers_most_complaint': [],
            'most_common_complaint': [],
            'race_count': [{
                'race': 'Asian',
                'count': 101
            }],
            'median_income': 343,
            'alderman': 'IronMan',
            'commander': None,
            'allegation_percentile': None,
            'police_hq': None
        })

    def test_extract_datum_police_district_has_no_description(self):
        area = AreaFactory(
            name='name',
            tags=['tag'],
            median_income=343,
            area_type='police-districts',
            alderman='IronMan',
        )

        expect(
            AreaIndexer().extract_datum(area)
        ).to.be.eq({
            'name': 'name',
            'url': area.v1_url,
            'area_type': 'police-district',
            'tags': ['tag', 'police district'],
            'allegation_count': 0,
            'officers_most_complaint': [],
            'most_common_complaint': [],
            'race_count': [],
            'median_income': 343,
            'alderman': 'IronMan',
            'commander': None,
            'allegation_percentile': None,
            'police_hq': None,
        })

    def test_extract_datum_with_officers_most_complaint(self):
        area = AreaFactory(
            name='name',
            tags=['tag'],
            median_income=343,
            area_type='police-districts',
            alderman='IronMan',
        )
        area.get_officers_most_complaints = Mock(return_value=[
            OfficerFactory.build(
                id=123,
                first_name='A',
                last_name='B',
                allegation_count=5,
                civilian_allegation_percentile=0,
                internal_allegation_percentile=0,
                trr_percentile=0,
                complaint_percentile=0
            ),
            OfficerFactory.build(
                id=456,
                first_name='E',
                last_name='F',
                allegation_count=3,
                civilian_allegation_percentile=Decimal(33.3333),
                internal_allegation_percentile=0,
                trr_percentile=Decimal(33.3333),
                complaint_percentile=Decimal(33.3333)
            ),
            OfficerFactory.build(
                id=999,
                first_name='X',
                last_name='Y',
                allegation_count=2,
                complaint_percentile=None
            )
        ])
        area_indexer = AreaIndexer()

        expect(area_indexer.extract_datum(area)).to.be.eq({
            'name': 'name',
            'url': area.v1_url,
            'area_type': 'police-district',
            'tags': ['tag', 'police district'],
            'allegation_count': 0,
            'most_common_complaint': [],
            'race_count': [],
            'median_income': 343,
            'alderman': 'IronMan',
            'commander': None,
            'allegation_percentile': None,
            'police_hq': None,
            'officers_most_complaint': [
                {
                    'id': 123,
                    'name': 'A B',
                    'count': 5,
                    'percentile_allegation_civilian': 0.0,
                    'percentile_allegation_internal': 0.0,
                    'percentile_trr': 0.0,
                    'percentile_allegation': 0.0,
                }, {
                    'id': 456,
                    'name': 'E F',
                    'count': 3,
                    'percentile_allegation_civilian': 33.3333,
                    'percentile_allegation_internal': 0.0,
                    'percentile_trr': 33.3333,
                    'percentile_allegation': 33.3333,
                }, {
                    'id': 999,
                    'name': 'X Y',
                    'count': 2
                }
            ],
        })


class IndexerManagerTestCase(SimpleTestCase):
    @patch('search.search_indexers.autocompletes_alias')
    def test_rebuild_index(self, autocompletes_alias):
        indexer_obj = Mock()
        indexer_obj.docs = Mock(return_value=[])
        indexer = Mock(return_value=indexer_obj)
        manager = IndexerManager(indexers=[indexer])
        manager.rebuild_index()

        expect(autocompletes_alias.write_index.close.called).to.be.true()
        expect(autocompletes_alias.migrate.called).to.be.true()
        expect(autocompletes_alias.indexing.return_value.__enter__.called).to.be.true()
        expect(autocompletes_alias.indexing.return_value.__exit__.called).to.be.true()
        expect(indexer.doc_type_klass.init.called).to.be.true()
        expect(indexer_obj.docs.called).to.be.true()


class CrIndexerTestCase(TestCase):
    def test_get_queryset(self):
        expect(CrIndexer().get_queryset().count()).to.eq(0)
        allegation = AllegationFactory(crid='123456', incident_date=datetime(2017, 7, 27, tzinfo=pytz.utc))
        officer = OfficerFactory()
        OfficerAllegationFactory(allegation=allegation, officer=officer)
        investigator = InvestigatorFactory(first_name='Jerome', last_name='Finnigan')
        InvestigatorAllegationFactory(investigator=investigator, allegation=allegation)

        querysets = CrIndexer().get_queryset()

        expect(querysets.count()).to.eq(1)
        allegation = querysets[0]
        expect(allegation.crid).to.eq('123456')
        expect(allegation.investigator_names).to.eq(['Jerome Finnigan'])

    def test_get_queryset_with_investigator_is_officer(self):
        allegation = AllegationFactory(
            crid='654321',
            incident_date=datetime(2009, 7, 27, tzinfo=pytz.utc),
            summary='abc')
        officer = OfficerFactory(id=10, first_name='Edward', last_name='May')
        OfficerAllegationFactory(allegation=allegation, officer=officer)
        investigator = InvestigatorFactory(officer=officer)
        InvestigatorAllegationFactory(investigator=investigator, allegation=allegation)

        querysets = CrIndexer().get_queryset()

        expect(querysets.count()).to.eq(1)
        allegation = querysets[0]
        expect(allegation.crid).to.eq('654321')
        expect(allegation.investigator_names).to.eq(['Edward May'])

    def test_extract_datum(self):
        allegation = AllegationFactory(
            crid='123456',
            incident_date=datetime(2017, 7, 27, tzinfo=pytz.utc),
            summary='abc',
            add1='3000',
            add2='Michigan Ave',
            city='Chicago IL'
        )
        officer = OfficerFactory(
            id=10,
            first_name='Luke',
            last_name='Skywalker',
            allegation_count=4,
            trr_percentile='99.88',
            civilian_allegation_percentile='77.66',
            internal_allegation_percentile='66.55'
        )
        officer2 = OfficerFactory(
            id=11,
            first_name='John', last_name='Doe',
            allegation_count=2,
            trr_percentile='66.88',
            civilian_allegation_percentile='33.66',
            internal_allegation_percentile='22.55'
        )
        OfficerAllegationFactory(allegation=allegation, officer=officer)

        category1 = AllegationCategoryFactory(
            category='Operation/Personnel Violations',
            allegation_name='Secondary/Special Employment'
        )
        category2 = AllegationCategoryFactory(category='Use of Force', allegation_name='sub category')
        OfficerAllegationFactory(allegation=allegation, allegation_category=category2, officer=officer2)
        OfficerAllegationFactory.create_batch(2, allegation=allegation, allegation_category=category1, officer=None)
        OfficerAllegationFactory.create_batch(3, allegation=allegation, allegation_category=None, officer=None)

        VictimFactory(allegation=allegation, gender='F', race='Black', age=25)
        VictimFactory(allegation=allegation, gender='', race='Black', age=25)
        VictimFactory(allegation=allegation, gender='F', race='Black', age=None)

        AttachmentFileFactory(id=1, allegation=allegation, text_content='')
        AttachmentFileFactory(
            id=2, allegation=allegation, show=False,
            text_content="CHICAGO POLICE DEPARTMENT RD I HT334604"
        )
        AttachmentFileFactory(id=3, allegation=allegation, text_content='CHICAGO POLICE DEPARTMENT RD I HT334604')

        setattr(allegation, 'investigator_names', ['Jerome Finnigan'])
        allegation_cache_manager.cache_data()
        allegation.refresh_from_db()

        datum = CrIndexer().extract_datum(allegation)
        datum['victims'] = sorted(
            datum['victims'],
            key=lambda victim: (victim['gender'], victim['race'], victim.get('age', 0))
        )

        expect(datum).to.eq({
            'crid': '123456',
            'category': 'Operation/Personnel Violations',
            'sub_category': 'Secondary/Special Employment',
            'incident_date': '2017-07-27',
            'address': '3000 Michigan Ave, Chicago IL',
            'summary': 'abc',
            'to': '/complaint/123456/',
            'investigator_names': ['Jerome Finnigan'],
            'victims': [
                {'gender': '', 'race': 'Black', 'age': 25},
                {'gender': 'Female', 'race': 'Black'},
                {'gender': 'Female', 'race': 'Black', 'age': 25},
            ],
            'coaccused': [
                {
                    'id': 10, 'full_name': 'Luke Skywalker', 'allegation_count': 4,
                    'percentile': {
                        'id': 10,
                        'percentile_trr': '99.8800',
                        'percentile_allegation_civilian': '77.6600',
                        'percentile_allegation_internal': '66.5500'
                    }
                },
                {
                    'id': 11, 'full_name': 'John Doe', 'allegation_count': 2,
                    'percentile': {
                        'id': 11,
                        'percentile_trr': '66.8800',
                        'percentile_allegation_civilian': '33.6600',
                        'percentile_allegation_internal': '22.5500'
                    }
                }
            ],
            'attachment_files': [
                {'id': 3, 'text_content': 'CHICAGO POLICE DEPARTMENT RD I HT334604'}
            ]
        })

    def test_extract_datum_with_missing_data(self):
        allegation = AllegationFactory(
            crid='123456',
            incident_date=None,
            summary='')
        OfficerAllegationFactory(allegation=allegation, officer=None, allegation_category=None)

        setattr(allegation, 'investigator_names', [])

        expect(
            CrIndexer().extract_datum(allegation)
        ).to.eq({
            'crid': '123456',
            'category': 'Unknown',
            'sub_category': 'Unknown',
            'incident_date': None,
            'summary': '',
            'address': '',
            'to': '/complaint/123456/',
            'investigator_names': [],
            'victims': [],
            'coaccused': [],
            'attachment_files': [],
        })


class TRRIndexerTestCase(TestCase):
    def test_get_queryset(self):
        indexer = TRRIndexer()
        expect(indexer.get_queryset().count()).to.eq(0)
        TRRFactory()
        expect(indexer.get_queryset().count()).to.eq(1)

    def test_extract_datum(self):
        trr = TRRFactory(id=123456, trr_datetime=datetime(2017, 7, 27, tzinfo=pytz.utc))
        ActionResponseFactory(trr=trr, force_type='Physical Force - Stunning', action_sub_category='4')
        ActionResponseFactory(trr=trr, force_type='Other', action_sub_category=None, person='Subject Action')
        ActionResponseFactory(trr=trr, force_type='Impact Weapon', action_sub_category='5.2')
        ActionResponseFactory(trr=trr, force_type='Taser Display', action_sub_category='3')

        expect(
            TRRIndexer().extract_datum(trr)
        ).to.eq({
            'id': 123456,
            'force_type': 'Impact Weapon',
            'trr_datetime': '2017-07-27',
            'to': '/trr/123456/'
        })

    def test_extract_datum_with_missing_trr_datetime_and_force_type(self):
        trr = TRRFactory(id='123456', trr_datetime=None)

        expect(
            TRRIndexer().extract_datum(trr)
        ).to.eq({
            'id': '123456',
            'force_type': None,
            'trr_datetime': None,
            'to': '/trr/123456/'
        })


class RankIndexerTestCase(TestCase):
    def test_get_queryset(self):
        expect(RankIndexer().get_queryset()).to.have.length(0)
        SalaryFactory(rank='Officer', officer__rank='Officer')
        OfficerFactory(rank='Detective')
        expect(RankIndexer().get_queryset()).to.have.length(2)

    def test_extract_datum(self):
        officer = OfficerFactory(rank='Police Officer', active=ACTIVE_YES_CHOICE)
        SalaryFactory(rank='Police Officer', officer=officer)

        expect(RankIndexer().extract_datum('Police Officer')).to.eq({
            'rank': 'Police Officer',
            'tags': ['rank'],
            'active_officers_count': 1,
            'officers_most_complaints': []
        })


class SearchTermItemIndexerTestCase(TestCase):
    def test_get_queryset(self):
        expect(SearchTermItemIndexer().get_queryset()).to.have.length(0)
        SearchTermItemFactory()
        expect(SearchTermItemIndexer().get_queryset()).to.have.length(1)

    def test_extract_datum(self):
        search_term_item = SearchTermItemFactory(
            slug='communities',
            name='Communities',
            category=SearchTermCategoryFactory(name='Geography'),
            description='Community description',
            call_to_action_type='view_all',
            link='/url-mediator/session-builder/?community=123456'
        )
        expect(SearchTermItemIndexer().extract_datum(search_term_item)).to.eq({
            'slug': 'communities',
            'name': 'Communities',
            'category_name': 'Geography',
            'description': 'Community description',
            'call_to_action_type': 'view_all',
            'link': '/url-mediator/session-builder/?community=123456',
        })
