from mock import Mock

from django.test import SimpleTestCase

from robber import expect

from search_mobile.formatters import OfficerV2Formatter, ReportFormatter, UnitFormatter


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


class UnitFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(
            meta=Mock(id='11'),
            url='https://data.cpdp.co/url-mediator/session-builder?unit=011',
            active_member_count=2,
            member_count=20
        )
        doc.name = '011'

        expect(
            UnitFormatter().doc_format(doc)
        ).to.be.eq({
            'id': 11,
            'text': '011',
            'url': 'https://data.cpdp.co/url-mediator/session-builder?unit=011',
            'active_member_count': 2,
            'member_count': 20
        })
