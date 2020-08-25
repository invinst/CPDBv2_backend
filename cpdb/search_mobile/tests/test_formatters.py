from datetime import datetime
import pytz

from django.test import SimpleTestCase
from django.test.testcases import TestCase

from robber import expect
from freezegun import freeze_time
from mock import Mock

from shared.tests.utils import create_object
from search_mobile.formatters import OfficerV2Formatter, TRRFormatter, CRFormatter, LawsuitFormatter
from search.doc_types import LawsuitDocType
from lawsuit.factories import LawsuitFactory


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


class LawsuitFormatterTestCase(TestCase):
    def test_get_queryset(self):
        lawsuit_1 = LawsuitFactory()
        lawsuit_2 = LawsuitFactory()
        LawsuitFactory()

        queryset = LawsuitFormatter().get_queryset([lawsuit_1.id, lawsuit_2.id])
        expect(
            {item.id for item in queryset}
        ).to.eq({lawsuit_1.id, lawsuit_2.id})

    def test_item_format(self):
        lawsuit = LawsuitFactory(
            case_no='00-L-5230',
            primary_cause='ILLEGAL SEARCH/SEIZURE',
            summary='Lawsuit Summary',
            incident_date=datetime(2002, 1, 3, tzinfo=pytz.utc)
        )

        expect(
            LawsuitFormatter().item_format(lawsuit)
        ).to.eq({
            'id': lawsuit.id,
            'case_no': '00-L-5230',
            'primary_cause': 'ILLEGAL SEARCH/SEIZURE',
            'summary': 'Lawsuit Summary',
            'incident_date': '2002-01-03'
        })

    def test_item_format_with_empty_incident_date(self):
        lawsuit = LawsuitFactory(
            case_no='00-L-5230',
            primary_cause='ILLEGAL SEARCH/SEIZURE',
            summary='Lawsuit Summary',
            incident_date=None
        )

        expect(
            LawsuitFormatter().item_format(lawsuit)['incident_date']
        ).to.be.none()

    def test_serialize(self):
        lawsuit_1 = LawsuitFactory(
            case_no='00-L-5230',
            primary_cause='ILLEGAL SEARCH/SEIZURE',
            summary='Lawsuit Summary 1',
            incident_date=datetime(2002, 1, 3, tzinfo=pytz.utc)

        )
        lawsuit_2 = LawsuitFactory(
            case_no='00-L-5231',
            primary_cause='FALSE ARREST',
            summary='Lawsuit Summary 2',
            incident_date=None
        )
        LawsuitFactory()

        result = LawsuitFormatter().serialize([LawsuitDocType(_id=lawsuit_1.id), LawsuitDocType(_id=lawsuit_2.id)])
        expected_result = [
            {
                'id': lawsuit_1.id,
                'case_no': '00-L-5230',
                'primary_cause': 'ILLEGAL SEARCH/SEIZURE',
                'summary': 'Lawsuit Summary 1',
                'incident_date': '2002-01-03'
            },
            {
                'id': lawsuit_2.id,
                'case_no': '00-L-5231',
                'primary_cause': 'FALSE ARREST',
                'summary': 'Lawsuit Summary 2',
                'incident_date': None
            }
        ]
        expect(result).to.eq(expected_result)
