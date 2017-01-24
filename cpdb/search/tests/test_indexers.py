from mock import Mock, patch

from robber import expect
from django.test import SimpleTestCase, TestCase

from ..indexers import (BaseIndexer, FAQIndexer, ReportIndexer, OfficerIndexer, UnitIndexer, AreaTypeIndexer,
                        NeighborhoodsIndexer, CommunityIndexer, IndexerManager)
from cms.factories import FAQPageFactory, ReportPageFactory
from data.factories import AreaFactory, OfficerFactory, OfficerBadgeNumberFactory, PoliceUnitFactory


class BaseIndexerTestCase(SimpleTestCase):
    def test_get_queryset(self):
        expect(lambda: BaseIndexer().get_queryset()).to.throw(NotImplementedError)

    def test_extract_datum(self):
        expect(lambda: BaseIndexer().extract_datum('anything')).to.throw(NotImplementedError)

    def test_index_datum(self):
        indexer = BaseIndexer()
        doc_type = Mock()
        indexer.doc_type_klass = Mock(return_value=doc_type)
        indexer.extract_datum = Mock(return_value={'key': 'something'})
        indexer.get_queryset = Mock(return_value=['something'])

        indexer.index_datum('anything')

        indexer.doc_type_klass.assert_called_once_with(key='something')
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
        datum = FAQPageFactory(question='question', answer=['answer1', 'answer2'])

        expect(
            FAQIndexer().extract_datum(datum)
        ).to.be.eq({
            'question': 'question',
            'answer': 'answer1\nanswer2'
        })


class ReportIndexerTestCase(TestCase):
    def test_get_queryset(self):
        expect(ReportIndexer().get_queryset().count()).to.eq(0)
        ReportPageFactory()
        expect(ReportIndexer().get_queryset().count()).to.eq(1)

    def test_extract_datum(self):
        datum = ReportPageFactory(
            publication='publication', author='author',
            title='title', excerpt=['excerpt1', 'excerpt2'])

        expect(
            ReportIndexer().extract_datum(datum)
        ).to.be.eq({
            'publication': 'publication',
            'author': 'author',
            'excerpt': 'excerpt1\nexcerpt2',
            'title': 'title'
        })


class OfficerIndexerTestCase(TestCase):
    def test_get_queryset(self):
        expect(OfficerIndexer().get_queryset().count()).to.eq(0)
        OfficerFactory()
        expect(OfficerIndexer().get_queryset().count()).to.eq(1)

    def test_extract_datum(self):
        datum = OfficerFactory(first_name='first', last_name='last')
        OfficerBadgeNumberFactory(officer=datum, star='123', current=True)

        expect(
            OfficerIndexer().extract_datum(datum)
        ).to.be.eq({
            'full_name': 'first last',
            'badge': '123',
            'url': datum.v1_url
        })


class UnitIndexerTestCase(TestCase):
    def test_get_queryset(self):
        expect(UnitIndexer().get_queryset().count()).to.eq(0)
        PoliceUnitFactory()
        expect(UnitIndexer().get_queryset().count()).to.eq(1)

    def test_extract_datum(self):
        datum = PoliceUnitFactory(unit_name='unit')

        expect(
            UnitIndexer().extract_datum(datum)
        ).to.be.eq({
            'name': 'unit',
            'url': datum.v1_url
        })


class AreaTypeIndexerTestCase(TestCase):
    def test_extract_datum(self):
        datum = AreaFactory(name='name')

        expect(
            AreaTypeIndexer().extract_datum(datum)
        ).to.be.eq({
            'name': 'name',
            'url': datum.v1_url
        })


class NeighborhoodsIndexerTestCase(TestCase):
    def test_get_queryset(self):
        AreaFactory(area_type='neighborhoods')
        AreaFactory(area_type='community')

        expect(NeighborhoodsIndexer().get_queryset()).to.have.length(1)
        expect(NeighborhoodsIndexer().get_queryset().first().area_type).to.be.eq('neighborhoods')


class CommunityIndexerTestCase(TestCase):
    def test_get_queryset(self):
        AreaFactory(area_type='neighborhoods')
        AreaFactory(area_type='community')

        expect(CommunityIndexer().get_queryset()).to.have.length(1)
        expect(CommunityIndexer().get_queryset().first().area_type).to.be.eq('community')


class IndexerManagerTestCase(SimpleTestCase):
    @patch('cpdb.search.indexers.autocompletes')
    def test_rebuild_index(self, autocompletes):
        indexer_obj = Mock()
        indexer = Mock(return_value=indexer_obj)

        manager = IndexerManager(indexers=[indexer])

        manager.rebuild_index()
        expect(autocompletes.delete.called).to.be.true()
        expect(autocompletes.create.called).to.be.true()
        expect(indexer_obj.index_data.called).to.be.true()
