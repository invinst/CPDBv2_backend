from mock import Mock

from django.test import SimpleTestCase

from robber import expect

from search_mobile.formatters import (
    OfficerV2Formatter, FAQFormatter, ReportFormatter
)


class OfficerV2FormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(
            full_name='name',
            badge='123',
            to='url',
            meta=Mock(id='333'),
        )

        expect(
            OfficerV2Formatter().doc_format(doc)
        ).to.be.eq({
            'id': 333,
            'name': 'name',
            'extra_info': 'Badge # 123',
            'url': 'url',
        })


class FAQFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(question='question', meta=Mock(id='111'))

        expect(
            FAQFormatter().doc_format(doc)
        ).to.be.eq({
            'question': 'question',
            'id': 111,
        })


class ReportFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(
            meta=Mock(id='9'),
            publication='publication',
            author='author',
            title='title',
            publish_date='2017-01-21',
        )

        expect(
            ReportFormatter().doc_format(doc)
        ).to.be.eq({
            'id': 9,
            'publication': 'publication',
            'title': 'title',
            'publish_date': '2017-01-21',
        })
