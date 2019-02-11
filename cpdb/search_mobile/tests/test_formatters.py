from mock import Mock

from django.test import SimpleTestCase

from robber import expect
from freezegun import freeze_time

from shared.tests.utils import create_object
from search_mobile.formatters import OfficerV2Formatter, TRRFormatter, CRFormatter


@freeze_time("2018-03-20")
class OfficerV2FormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        officer_dict = {
            'full_name': 'name',
            'badge': '123',
            'id': '333',
            'percentiles': [
                {
                    'a': 1,
                    'year': 2001,
                },
                {
                    'b': 2,
                    'year': 2016
                },
                {
                    'c': 3,
                    'year': 2019
                }
            ]
        }
        doc = Mock(to_dict=Mock(return_value=officer_dict))

        expect(
            OfficerV2Formatter().doc_format(doc)
        ).to.be.eq({
            'id': 333,
            'name': 'name',
            'badge': '123',
            'percentile': {
                'b': 2,
                'year': 2016
            }
        })

    def test_doc_format_with_no_percentiles(self):
        officer_dict = {
            'full_name': 'name',
            'badge': '123',
            'id': '333',
            'percentiles': []
        }
        doc = Mock(to_dict=Mock(return_value=officer_dict))

        expect(
            OfficerV2Formatter().doc_format(doc)
        ).to.be.eq({
            'id': 333,
            'name': 'name',
            'badge': '123',
            'percentile': []
        })


class CRFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        cr = Mock(crid='123', incident_date='2013-04-13', category='Domestic')
        expect(
            CRFormatter().doc_format(cr)
        ).to.be.eq({
            'crid': '123',
            'incident_date': '2013-04-13',
            'category': 'Domestic'
        })

        no_category_cr = create_object({'crid': '123', 'incident_date': '2013-04-13'})
        expect(
            CRFormatter().doc_format(no_category_cr)
        ).to.be.eq({
            'crid': '123',
            'incident_date': '2013-04-13',
            'category': 'Unknown'
        })


class TRRFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        trr_dict = {
            'id': '123'
        }
        doc = Mock(to_dict=Mock(return_value=trr_dict))

        expect(
            TRRFormatter().doc_format(doc)
        ).to.be.eq({
            'id': '123'
        })
