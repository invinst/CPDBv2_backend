from mock import Mock

from django.test import SimpleTestCase

from robber import expect

from search.formatters import (
    SimpleFormatter, OfficerFormatter, NameFormatter, OfficerV2Formatter,
    NameV2Formatter, FAQFormatter, ReportFormatter, Formatter, CoAccusedOfficerFormatter, UnitFormatter)


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
        doc1 = Mock(
            to_dict=Mock(return_value={'a': 'a'}),
            _id='a_id'
        )
        doc2 = Mock(
            to_dict=Mock(return_value={'b': 'b'}),
            _id='b_id'
        )
        response = Mock(hits=[doc1, doc2])

        expect(
            SimpleFormatter().format(response)
        ).to.be.eq([{'a': 'a', 'id': 'a_id'}, {'b': 'b', 'id': 'b_id'}])


class OfficerFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'full_name': 'name',
            'badge': '123',
            'to': 'to',
            'tags': ['tag1', 'tag2']
        }))

        expect(
            OfficerFormatter().doc_format(doc)
        ).to.be.eq({
            'text': 'name',
            'payload': {
                'result_text': 'name',
                'result_extra_information': 'Badge # 123',
                'to': 'to',
                'result_reason': 'tag1, tag2',
                'tags': ['tag1', 'tag2']
            }
        })


class CoAccusedOfficerFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'full_name': 'name',
            'badge': '123',
            'to': 'to',
            'co_accused_officer': {
                'full_name': 'David Beckham',
                'badge': '7'
            }
        }))

        expect(
            CoAccusedOfficerFormatter().doc_format(doc)
        ).to.be.eq({
            'text': 'name',
            'payload': {
                'result_text': 'name',
                'result_extra_information': 'Badge # 123',
                'to': 'to',
                'result_reason': 'coaccused with David Beckham (7)'
            }
        })


class UnitFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(description='123', url='url')
        doc.name = 'name'

        expect(
            UnitFormatter().doc_format(doc)
        ).to.be.eq({
            'text': 'name',
            'payload': {
                'result_text': 'name',
                'result_extra_information': '123',
                'url': 'url'
            }
        })


class NameFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(url='url', tags=['t1', 't2'])
        doc.name = 'name'

        expect(
            NameFormatter().doc_format(doc)
        ).to.be.eq({
            'text': 'name',
            'payload': {
                'result_text': 'name',
                'url': 'url',
                'tags': ['t1', 't2']
            },
        })


class OfficerV2FormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(full_name='name', tags=['t1', 't2'], badge='123', to='to')

        expect(
            OfficerV2Formatter().doc_format(doc)
        ).to.be.eq({
            'result_text': 'name',
            'result_extra_information': 'Badge # 123',
            'to': 'to',
            'tags': ['t1', 't2']
        })


class NameV2FormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(url='url', tags=['t1', 't2'])
        doc.name = 'name'

        expect(
            NameV2Formatter().doc_format(doc)
        ).to.be.eq({
            'result_text': 'name',
            'url': 'url',
            'tags': ['t1', 't2']
        })


class FAQFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(question='question', answer='answer', tags=['t1', 't2'])

        expect(
            FAQFormatter().doc_format(doc)
        ).to.be.eq({
            'question': 'question',
            'answer': 'answer',
            'tags': ['t1', 't2']
        })


class ReportFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(
            publication='publication',
            author='author',
            title='title',
            excerpt='excerpt',
            tags=['t1', 't2']
        )

        expect(
            ReportFormatter().doc_format(doc)
        ).to.be.eq({
            'publication': 'publication',
            'author': 'author',
            'title': 'title',
            'excerpt': 'excerpt',
            'tags': ['t1', 't2']
        })
