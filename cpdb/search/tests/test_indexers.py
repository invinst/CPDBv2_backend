from mock import Mock, patch

from robber import expect
from django.test import SimpleTestCase, TestCase

from search.search_indexers import CrIndexer
from ..search_indexers import BaseIndexer, UnitIndexer, AreaIndexer, IndexerManager
from data.factories import (
    AreaFactory, OfficerFactory, PoliceUnitFactory,
    OfficerHistoryFactory, AllegationFactory,
    OfficerAllegationFactory, RacePopulationFactory)

from search.search_indexers import autocompletes_alias


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

    def test_index_datum_dict(self):
        with patch.object(autocompletes_alias, 'new_index_name', 'test_autocompletes_1'):
            indexer = BaseIndexer()
            doc_type = Mock()
            indexer.doc_type_klass = Mock(return_value=doc_type)
            indexer.extract_datum_with_id = Mock(return_value={'key': 'something'})
            indexer.get_queryset = Mock(return_value=['something'])

            indexer.index_datum('anything')

            indexer.doc_type_klass.assert_called_once_with(key='something', _index='test_autocompletes_1')
            expect(doc_type.save.called).to.be.true()

    def test_index_datum_list(self):
        with patch.object(autocompletes_alias, 'new_index_name', 'test_autocompletes_1'):
            indexer = BaseIndexer()

            doc_type = Mock()
            indexer.doc_type_klass = Mock(return_value=doc_type)
            indexer.extract_datum_with_id = Mock(return_value=[{'key': 'something'}])
            indexer.get_queryset = Mock(return_value=['something'])

            indexer.index_datum('anything')
            indexer.doc_type_klass.assert_called_once_with(key='something', _index='test_autocompletes_1')
            expect(doc_type.save.called).to.be.true()

    def test_index_data(self):
        indexer = BaseIndexer()
        indexer.get_queryset = Mock(return_value=[1])
        indexer.doc_type_klass = Mock()
        indexer.index_datum = Mock()

        indexer.index_data()

        indexer.index_datum.assert_called_once_with(1)


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
            'member_count': 2
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
        AllegationFactory.create_batch(1, areas=[area2])

        area_indexer = AreaIndexer()
        expect(area_indexer.get_queryset().count()).to.eq(2)
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
                'count': 5
            }, {
                'id': 456,
                'name': 'E F',
                'count': 3
            }, {
                'id': 789,
                'name': 'C D',
                'count': 2
            }
        ])
        area_indexer = AreaIndexer()
        area_indexer.top_percentile_dict = {
            123: {
                'percentile_allegation_civilian': 0,
                'percentile_allegation_internal': 0,
                'percentile_trr': 0,
                'percentile_allegation': 0,
            },
            456: {
                'percentile_allegation_civilian': 33.3333,
                'percentile_allegation_internal': 0,
                'percentile_trr': 33.3333,
                'percentile_allegation': 33.3333,
            },
            789: {
                'percentile_allegation_civilian': 66.6667,
                'percentile_allegation_internal': 0,
                'percentile_trr': 66.6667,
                'percentile_allegation': 66.6667,
            },
        }

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
                }
            ],
        })


class IndexerManagerTestCase(SimpleTestCase):
    @patch('cpdb.search.search_indexers.autocompletes_alias')
    def test_rebuild_index(self, autocompletes_alias):
        indexer_obj = Mock()
        indexer = Mock(return_value=indexer_obj)
        manager = IndexerManager(indexers=[indexer])
        manager.rebuild_index()

        expect(autocompletes_alias.write_index.close.called).to.be.true()
        expect(autocompletes_alias.migrate.called).to.be.true()
        expect(autocompletes_alias.indexing.return_value.__enter__.called).to.be.true()
        expect(autocompletes_alias.indexing.return_value.__exit__.called).to.be.true()
        expect(indexer.doc_type_klass.init.called).to.be.true()
        expect(indexer_obj.index_data.called).to.be.true()


class CrIndexerTestCase(TestCase):
    def test_get_queryset(self):
        expect(CrIndexer().get_queryset().count()).to.eq(0)
        allegation = AllegationFactory()
        officer = OfficerFactory()
        OfficerAllegationFactory(allegation=allegation, officer=officer)
        expect(CrIndexer().get_queryset().count()).to.eq(1)

    def test_extract_datum(self):
        allegation = AllegationFactory(crid='123456')
        officer = OfficerFactory(id=10)
        OfficerAllegationFactory(allegation=allegation, officer=officer)

        expect(
            CrIndexer().extract_datum(allegation)
        ).to.eq({
            'crid': '123456',
            'to': '/complaint/123456/10/'
        })
