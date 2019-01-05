from mock import Mock, patch
from datetime import datetime

from django.test import SimpleTestCase, TestCase

from robber import expect
import pytz

from data.constants import ACTIVE_YES_CHOICE
from data.models import Salary
from search.search_indexers import (
    CrIndexer, TRRIndexer, BaseIndexer, UnitIndexer, AreaIndexer, IndexerManager, RankIndexer
)
from data.factories import (
    AreaFactory, OfficerFactory, PoliceUnitFactory,
    OfficerHistoryFactory, AllegationFactory,
    OfficerAllegationFactory, RacePopulationFactory,
    SalaryFactory, AllegationCategoryFactory)
from trr.factories import TRRFactory, ActionResponseFactory


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
            {
                'id': 123,
                'name': 'A B',
                'count': 5,
                'percentile_allegation_civilian': 0,
                'percentile_allegation_internal': 0,
                'percentile_trr': 0,
                'percentile_allegation': 0,
            }, {
                'id': 456,
                'name': 'E F',
                'count': 3,
                'percentile_allegation_civilian': 33.3333,
                'percentile_allegation_internal': 0,
                'percentile_trr': 33.3333,
                'percentile_allegation': 33.3333,
            }, {
                'id': 789,
                'name': 'C D',
                'count': 2,
                'percentile_allegation_civilian': 66.6667,
                'percentile_allegation_internal': 0,
                'percentile_trr': 66.6667,
                'percentile_allegation': 66.6667,
            }, {
                'id': 999,
                'name': 'X Y',
                'count': 2
            }
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
                    'percentile_allegation_civilian': 0,
                    'percentile_allegation_internal': 0,
                    'percentile_trr': 0,
                    'percentile_allegation': 0,
                }, {
                    'id': 456,
                    'name': 'E F',
                    'count': 3,
                    'percentile_allegation_civilian': 33.3333,
                    'percentile_allegation_internal': 0,
                    'percentile_trr': 33.3333,
                    'percentile_allegation': 33.3333,
                }, {
                    'id': 789,
                    'name': 'C D',
                    'count': 2,
                    'percentile_allegation_civilian': 66.6667,
                    'percentile_allegation_internal': 0,
                    'percentile_trr': 66.6667,
                    'percentile_allegation': 66.6667,
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
        allegation = AllegationFactory(incident_date=datetime(2017, 7, 27, tzinfo=pytz.utc))
        officer = OfficerFactory()
        OfficerAllegationFactory(allegation=allegation, officer=officer)
        expect(CrIndexer().get_queryset().count()).to.eq(1)

    def test_extract_datum(self):
        allegation = AllegationFactory(crid='123456', incident_date=datetime(2017, 7, 27, tzinfo=pytz.utc))
        officer = OfficerFactory(id=10)
        OfficerAllegationFactory(allegation=allegation, officer=officer)

        category1 = AllegationCategoryFactory(category='Abc')
        category2 = AllegationCategoryFactory(category='Def')
        OfficerAllegationFactory(allegation=allegation, allegation_category=category2)
        OfficerAllegationFactory.create_batch(2, allegation=allegation, allegation_category=category1)
        OfficerAllegationFactory.create_batch(3, allegation=allegation, allegation_category=None)

        expect(
            CrIndexer().extract_datum(allegation)
        ).to.eq({
            'crid': '123456',
            'category': 'Abc',
            'incident_date': '2017-07-27',
            'to': '/complaint/123456/'
        })

    def test_extract_datum_with_missing_incident_date_and_category(self):
        allegation = AllegationFactory(crid='123456', incident_date=None)
        officer = OfficerFactory(id=10)
        OfficerAllegationFactory(allegation=allegation, officer=officer, allegation_category=None)

        expect(
            CrIndexer().extract_datum(allegation)
        ).to.eq({
            'crid': '123456',
            'category': None,
            'incident_date': None,
            'to': '/complaint/123456/'
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

        expect(RankIndexer().extract_datum(Salary.objects.rank_objects[0])).to.eq({
            'rank': 'Police Officer',
            'tags': ['rank'],
            'active_officers_count': 1,
            'officers_most_complaints': []
        })
