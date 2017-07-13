from mock import Mock
from robber import expect
from django.test import SimpleTestCase

from cpdb.alias.utils import set_aliases


class AliasUtilsTestCase(SimpleTestCase):
    def test_set_aliases(self):
        document = Mock()
        record = Mock()
        queryset = Mock(get=Mock(return_value=record))

        class TestIndexer:
            doc_type_klass = Mock(get=Mock(return_value=document))
            get_queryset = Mock(return_value=queryset)

        set_aliases(TestIndexer, 'pk', ['alias1', 'alias2'])

        expect(TestIndexer.doc_type_klass.get).to.be.called_once_with('pk')
        expect(TestIndexer.get_queryset).to.be.called_once()
        expect(queryset.get).to.be.called_once()
        expect(record.tags).to.eq(['alias1', 'alias2'])
        expect(record.save).to.be.called_once()
        document.update.assert_called_once_with(tags=['alias1', 'alias2'])
