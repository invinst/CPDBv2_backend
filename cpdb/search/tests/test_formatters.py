from mock import Mock

from django.test import SimpleTestCase

from robber import expect

from search.formatters import (
    SimpleFormatter, OfficerFormatter, NameFormatter, OfficerV2Formatter,
    NameV2Formatter, FAQFormatter, ReportFormatter, Formatter)


class FormatterTestCase(SimpleTestCase):
    def test_format(self):
        expect(Formatter().format).to.throw(NotImplementedError)


class SimpleFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value='a'))

        expect(
            SimpleFormatter().doc_format(doc)
        ).to.be.equal('a')

    def test_format(self):
        doc1 = Mock(to_dict=Mock(return_value='a'))
        doc2 = Mock(to_dict=Mock(return_value='b'))
        response = Mock(hits=[doc1, doc2])

        expect(
            SimpleFormatter().format(response)
        ).to.be.eq(['a', 'b'])


class OfficerFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'full_name': 'name',
            'badge': '123',
            'url': 'url',
            'tags': ['tag']
        }))

        expect(
            OfficerFormatter().doc_format(doc)
        ).to.be.eq({
            'text': 'name',
            'payload': {
                'result_text': 'name',
                'result_extra_information': 'Badge # 123',
                'url': 'url',
                'tags': ['tag']
            }
        })


class NameFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(url='url')
        doc.name = 'name'

        expect(
            NameFormatter().doc_format(doc)
        ).to.be.eq({
            'text': 'name',
            'payload': {
                'result_text': 'name',
                'url': 'url'
            }
        })


class OfficerV2FormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(full_name='name', badge='123', url='url')

        expect(
            OfficerV2Formatter().doc_format(doc)
        ).to.be.eq({
            'result_text': 'name',
            'result_extra_information': 'Badge # 123',
            'url': 'url'
        })


class NameV2FormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(url='url')
        doc.name = 'name'

        expect(
            NameV2Formatter().doc_format(doc)
        ).to.be.eq({
            'result_text': 'name',
            'url': 'url'
        })


class FAQFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(question='question', answer='answer')

        expect(
            FAQFormatter().doc_format(doc)
        ).to.be.eq({
            'question': 'question',
            'answer': 'answer'
        })


class ReportFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(publication='publication', author='author', title='title', excerpt='excerpt')

        expect(
            ReportFormatter().doc_format(doc)
        ).to.be.eq({
            'publication': 'publication',
            'author': 'author',
            'title': 'title',
            'excerpt': 'excerpt'
        })
