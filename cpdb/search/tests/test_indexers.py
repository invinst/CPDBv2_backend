from mock import Mock, patch

from robber import expect
from django.test import SimpleTestCase, TestCase

from search.search_indexers import CrIndexer
from ..search_indexers import (
    BaseIndexer, FAQIndexer, ReportIndexer, OfficerIndexer, UnitIndexer, AreaIndexer,
    IndexerManager, UnitOfficerIndexer
)
from cms.factories import FAQPageFactory, ReportPageFactory
from data.factories import (
    AreaFactory, OfficerFactory, OfficerBadgeNumberFactory, PoliceUnitFactory,
    OfficerHistoryFactory, AllegationFactory,
    OfficerAllegationFactory, RacePopulationFactory)

from search.search_indexers import autocompletes_alias


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


class FAQIndexerTestCase(TestCase):
    def test_get_queryset(self):
        expect(FAQIndexer().get_queryset().count()).to.eq(0)
        FAQPageFactory()
        expect(FAQIndexer().get_queryset().count()).to.eq(1)

    def test_extract_datum(self):
        datum = FAQPageFactory(
            question='question',
            answer=['answer1', 'answer2']
        )

        expect(
            FAQIndexer().extract_datum(datum)
        ).to.be.eq({
            'question': 'question',
            'answer': 'answer1\nanswer2',
            'tags': []
        })


class ReportIndexerTestCase(TestCase):
    def test_get_queryset(self):
        expect(ReportIndexer().get_queryset().count()).to.eq(0)
        ReportPageFactory()
        expect(ReportIndexer().get_queryset().count()).to.eq(1)

    def test_extract_datum(self):
        datum = ReportPageFactory(
            publication='publication', author='author',
            title='title', excerpt=['excerpt1', 'excerpt2'],
            publish_date='2017-12-20'
        )
        expect(
            ReportIndexer().extract_datum(datum)
        ).to.be.eq({
            'publication': 'publication',
            'author': 'author',
            'excerpt': 'excerpt1\nexcerpt2',
            'title': 'title',
            'publish_date': '2017-12-20',
            'tags': [],
        })


class OfficerIndexerTestCase(TestCase):
    def test_get_queryset(self):
        expect(OfficerIndexer().get_queryset().count()).to.eq(0)
        OfficerFactory()
        expect(OfficerIndexer().get_queryset().count()).to.eq(1)

    def test_extract_datum(self):
        datum = OfficerFactory(
            first_name='first',
            last_name='last',
            tags=['tag1', 'tag2'],
            rank='some rank',
            race='some race',
            birth_year=1980,
            gender='M'
        )
        OfficerAllegationFactory.create_batch(10, final_finding='NS', officer=datum)
        unit = PoliceUnitFactory(unit_name='011')
        OfficerHistoryFactory(officer=datum, unit=unit)
        OfficerBadgeNumberFactory(officer=datum, star='123', current=True)

        expect(
            OfficerIndexer().extract_datum(datum)
        ).to.be.eq({
            'allegation_count': 10,
            'sustained_count': 0,
            'birth_year': 1980,
            'full_name': 'first last',
            'badge': '123',
            'to': datum.v2_to,
            'tags': ['tag1', 'tag2'],
            'visual_token_background_color': '#c6d4ec',
            'unit': '011',
            'rank': 'some rank',
            'race': 'some race',
            'sex': 'Male'
        })


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
    def setUp(self):
        self.area = AreaFactory(name='name', tags=['tag'], median_income=343, area_type='police-districts')
        RacePopulationFactory(area=self.area, race='Asian', count=101)

    def test_extract_datum(self):

        expect(
            AreaIndexer().extract_datum(self.area)
        ).to.be.eq({
            'name': 'name',
            'url': self.area.v1_url,
            'area_type': 'police-district',
            'tags': ['tag', 'police district'],
            'allegation_count': 0,
            'officers_most_complaint': [],
            'most_common_complaint': [],
            'race_count': [{
                'race': 'Asian',
                'count': 101
            }],
            'median_income': 343,
        })

    def test_get_queryset(self):
        expect(AreaIndexer().get_queryset()).to.have.length(1)


class UnitOfficerIndexerTestCase(TestCase):
    def setUp(self):
        unit = PoliceUnitFactory(unit_name='001', description='Something')
        officer = OfficerFactory(
            first_name='Kevin', last_name='Osborn', rank='somebody', race='White', gender='M', birth_year=1944
        )
        OfficerAllegationFactory.create_batch(10, final_finding='NS', officer=officer)
        self.history = OfficerHistoryFactory(unit=unit, officer=officer)

    def test_get_queryset(self):
        expect(UnitOfficerIndexer().get_queryset()).to.have.length(1)

    def test_extract_datum(self):
        expect(UnitOfficerIndexer().extract_datum(self.history)).to.eq({
            'full_name': 'Kevin Osborn',
            'badge': '',
            'to': self.history.officer.v2_to,
            'allegation_count': 10,
            'sustained_count': 0,
            'birth_year': 1944,
            'unit_name': '001',
            'unit_description': 'Something',
            'unit': '001',
            'rank': 'somebody',
            'race': 'White',
            'sex': 'Male',
            'visual_token_background_color': '#c6d4ec'
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
