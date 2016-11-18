from django.test import SimpleTestCase

from suggestion.indexers import AutoCompleteIndexer


class IndexersTestCase(SimpleTestCase):
    def setUp(self):
        self.indexer = AutoCompleteIndexer()

    def test_prefix_tokenizer(self):
        self.assertListEqual(list(self.indexer._prefix_tokenize('abc')), ['abc'])
        self.assertListEqual(
            list(self.indexer._prefix_tokenize('a b c d e f g h i j k')),
            [
                'a b c d e f g h i j',
                'b c d e f g h i j k',
                'c d e f g h i j k',
                'd e f g h i j k',
                'e f g h i j k',
                'f g h i j k',
                'g h i j k',
                'h i j k',
                'i j k',
                'j k',
                'k',
            ])
