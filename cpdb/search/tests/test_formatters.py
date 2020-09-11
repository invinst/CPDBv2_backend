from datetime import datetime
import pytz

from django.test import SimpleTestCase
from django.test.testcases import TestCase
from elasticsearch_dsl.utils import AttrDict, AttrList
from mock import Mock, patch
from robber import expect

from search.formatters import (
    SimpleFormatter, DataFormatter, OfficerFormatter, OfficerV2Formatter,
    NameV2Formatter, ReportFormatter, Formatter, UnitFormatter, CRFormatter, TRRFormatter,
    AreaFormatter, RankFormatter, ZipCodeFormatter, SearchTermFormatter, LawsuitFormatter,
)
from search.doc_types import LawsuitDocType
from lawsuit.factories import LawsuitFactory


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
            _id='a_id',
            meta=Mock(spec=[])
        )
        doc2 = Mock(
            to_dict=Mock(return_value={'b': 'b'}),
            _id='b_id',
            meta=Mock(
                highlight=AttrDict({
                    'abc': AttrList([
                        'struck <em>gun</em> on victims head.'
                    ])
                })
            )
        )
        response = Mock(hits=[doc1, doc2])

        expect(
            SimpleFormatter().format(response)
        ).to.be.eq([
            {'a': 'a', 'id': 'a_id'},
            {'b': 'b', 'id': 'b_id', 'highlight': {
                'abc': ['struck <em>gun</em> on victims head.']
            }}
        ])

    def test_serialize(self):
        doc = Mock(
            to_dict=Mock(return_value={'a': 'a'}),
            _id='a_id',
            meta=Mock(spec=[])
        )
        expect(SimpleFormatter().serialize([doc])).to.eq([{
            'a': 'a',
            'id': 'a_id'
        }])


class DataFormatterTestCase(SimpleTestCase):
    def test_get_queryset(self):
        expect(lambda: DataFormatter().get_queryset([])).to.throw(NotImplementedError)

    @patch('search.formatters.DataFormatter.serialize', return_value='serialize_data')
    def test_format(self, serialize_mock):
        docs = [Mock(_id='a_id'), Mock(_id='b_id')]
        response = Mock(hits=docs)

        expect(DataFormatter().format(response)).to.eq('serialize_data')

        serialize_mock.assert_called_with(docs)


class OfficerFormatterTestCase(SimpleTestCase):
    def test_officer_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'id': 1,
            'full_name': 'name',
            'badge': '123',
            'to': 'to',
            'tags': ['tag1', 'tag2'],
            'allegation_count': 10,
            'sustained_count': 2,
            'date_of_appt': '1998-01-01',
            'visual_token_background_color': '#ffffff',
            'unit': '001',
            'rank': 'some rank',
            'birth_year': 1972,
            'race': 'White',
            'gender': 'Male',
            'honorable_mention_count': 3,
            'annotated_trr_count': 1,
            'major_award_count': 1,
            'honorable_mention_percentile': 10,
            'complaint_percentile': 99.345,
            'civilian_allegation_percentile': 99.784,
            'internal_allegation_percentile': 88.342,
            'trr_percentile': 77.145,
        }))

        expect(
            OfficerFormatter().doc_format(doc)
        ).to.be.eq({
            'name': 'name',
            'badge': '123',
            'to': 'to',
            'tags': ['tag1', 'tag2'],
            'unit': '001',
            'appointed_date': '1998-01-01',
            'resignation_date': None,
            'trr_count': 1,
            'rank': 'some rank',
            'allegation_count': 10,
            'sustained_count': 2,
            'discipline_count': 0,
            'honorable_mention_count': 3,
            'civilian_compliment_count': 0,
            'race': 'White',
            'birth_year': 1972,
            'gender': 'Male',
            'major_award_count': 1,
            'honorable_mention_percentile': 10,
            'percentile_allegation': 99.345,
            'percentile_allegation_civilian': 99.784,
            'percentile_allegation_internal': 88.342,
            'percentile_trr': 77.145
        })

    def test_officer_doc_format_with_missing_values(self):
        doc = Mock(to_dict=Mock(return_value={
            'id': 1,
            'full_name': 'name',
        }))

        expect(
            OfficerFormatter().doc_format(doc)
        ).to.be.eq({
            'name': 'name',
            'badge': None,
            'to': None,
            'tags': [],
            'unit': None,
            'appointed_date': None,
            'resignation_date': None,
            'trr_count': 0,
            'rank': None,
            'allegation_count': 0,
            'sustained_count': 0,
            'discipline_count': 0,
            'honorable_mention_count': 0,
            'civilian_compliment_count': 0,
            'race': None,
            'birth_year': None,
            'gender': None,
            'major_award_count': 0,
            'honorable_mention_percentile': None,
            'percentile_allegation': None,
            'percentile_allegation_civilian': None,
            'percentile_allegation_internal': None,
            'percentile_trr': None
        })


class UnitFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock()
        doc.to_dict = Mock(return_value={
            'name': '123',
            'description': 'foo bar',
            'to': '/unit/123/',
            'tags': ['foo']
        })

        expect(
            UnitFormatter().doc_format(doc)
        ).to.be.eq({
            'description': 'foo bar',
            'to': '/unit/123/',
            'tags': ['foo'],
            'name': '123'
        })

    def test_doc_format_without_tags(self):
        doc = Mock()
        doc.to_dict = Mock(return_value={
            'name': '123',
            'description': 'foo bar',
            'to': '/unit/123/'
        })

        expect(
            UnitFormatter().doc_format(doc)
        ).to.be.eq({
            'description': 'foo bar',
            'to': '/unit/123/',
            'tags': [],
            'name': '123',
        })

    def test_doc_format_without_description(self):
        doc = Mock()
        doc.to_dict = Mock(return_value={
            'name': '123',
            'to': '/unit/123/',
            'tags': ['foo']
        })

        expect(
            UnitFormatter().doc_format(doc)
        ).to.be.eq({
            'description': '',
            'to': '/unit/123/',
            'tags': ['foo'],
            'name': '123'
        })


class OfficerV2FormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'full_name': 'name',
            'tags': ['t1', 't2'],
            'badge': '123',
            'to': 'to'
        }))

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
        doc = Mock(to_dict=Mock(return_value={
            'url': 'url',
            'tags': ['t1', 't2'],
            'name': 'name'
        }))

        expect(
            NameV2Formatter().doc_format(doc)
        ).to.be.eq({
            'result_text': 'name',
            'url': 'url',
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


class CrFormatterTestCase(SimpleTestCase):
    def test_process_doc(self):
        doc = Mock(
            crid='123456',
            to='/complaint/123456/',
            summary='abc',
            _id='123',
            incident_date='1990-01-02',
            meta=Mock(
                highlight=AttrDict({
                    'summary': AttrList([
                        'fired a <em>gun</em> at the victims',
                        'struck Victim B on the head with a <em>gun</em>'
                    ])
                }),
                inner_hits=Mock(
                    attachment_files=Mock(hits=[
                        Mock(
                            meta=Mock(highlight={
                                'attachment_files.text_content': [
                                    'a <em>gun</em> is fired',
                                    'struck Victim A on the head with a <em>gun</em>'
                                ]
                            })
                        ),
                        Mock()
                    ])
                )
            ),
            category='Operation/Personnel Violations',
            sub_category='Secondary/Special Employment',
            address='3000 Michigan Ave, Chicago IL',
            victims=[
                Mock(to_dict=Mock(return_value={'gender': '', 'race': 'Black', 'age': 25})),
                Mock(to_dict=Mock(return_value={'gender': 'Female', 'race': 'Black'})),
                Mock(to_dict=Mock(return_value={'gender': 'Female', 'race': 'Black', 'age': 25}))
            ],
            coaccused=[
                Mock(to_dict=Mock(return_value={
                    'id': 10, 'full_name': 'Luke Skywalker', 'allegation_count': 4,
                    'percentile_allegation': '79.6600',
                    'percentile_allegation_civilian': '77.6600',
                    'percentile_allegation_internal': '66.5500',
                    'percentile_trr': '99.8800'
                }))
            ]
        )

        expect(
            CRFormatter().process_doc(doc)
        ).to.eq({
            'crid': '123456',
            'to': '/complaint/123456/',
            'id': '123',
            'incident_date': '1990-01-02',
            'highlight': {
                'summary': [
                    'fired a <em>gun</em> at the victims',
                    'struck Victim B on the head with a <em>gun</em>'
                ],
                'text_content': [
                    'a <em>gun</em> is fired',
                    'struck Victim A on the head with a <em>gun</em>'
                ]
            },
            'category': 'Operation/Personnel Violations',
            'sub_category': 'Secondary/Special Employment',
            'address': '3000 Michigan Ave, Chicago IL',
            'victims': [
                {'gender': '', 'race': 'Black', 'age': 25},
                {'gender': 'Female', 'race': 'Black'},
                {'gender': 'Female', 'race': 'Black', 'age': 25},
            ],
            'coaccused': [
                {
                    'id': 10, 'full_name': 'Luke Skywalker', 'allegation_count': 4,
                    'percentile_allegation': '79.6600',
                    'percentile_allegation_civilian': '77.6600',
                    'percentile_allegation_internal': '66.5500',
                    'percentile_trr': '99.8800'
                }
            ]
        })

    def test_process_doc_no_highlight(self):
        doc = Mock(
            crid='123456',
            to='/complaint/123456/',
            summary='abc',
            _id='123',
            incident_date='1990-01-02',
            meta=Mock(highlight=None, inner_hits=None),
            category='Operation/Personnel Violations',
            sub_category='Secondary/Special Employment',
            address='3000 Michigan Ave, Chicago IL',
            victims=[
                Mock(to_dict=Mock(return_value={'gender': '', 'race': 'Black', 'age': 25})),
                Mock(to_dict=Mock(return_value={'gender': 'Female', 'race': 'Black'})),
                Mock(to_dict=Mock(return_value={'gender': 'Female', 'race': 'Black', 'age': 25}))
            ],
            coaccused=[
                Mock(to_dict=Mock(return_value={
                    'id': 10, 'full_name': 'Luke Skywalker', 'allegation_count': 4,
                    'percentile_allegation': '79.6600',
                    'percentile_allegation_civilian': '77.6600',
                    'percentile_allegation_internal': '66.5500',
                    'percentile_trr': '99.8800',
                }))
            ]
        )

        expect(
            CRFormatter().process_doc(doc)
        ).to.eq({
            'crid': '123456',
            'to': '/complaint/123456/',
            'id': '123',
            'incident_date': '1990-01-02',
            'category': 'Operation/Personnel Violations',
            'sub_category': 'Secondary/Special Employment',
            'address': '3000 Michigan Ave, Chicago IL',
            'victims': [
                {'gender': '', 'race': 'Black', 'age': 25},
                {'gender': 'Female', 'race': 'Black'},
                {'gender': 'Female', 'race': 'Black', 'age': 25},
            ],
            'coaccused': [
                {
                    'id': 10, 'full_name': 'Luke Skywalker', 'allegation_count': 4,
                    'percentile_allegation': '79.6600',
                    'percentile_allegation_civilian': '77.6600',
                    'percentile_allegation_internal': '66.5500',
                    'percentile_trr': '99.8800',
                }
            ]
        })


class TRRFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'id': '123456',
            'to': '/trr/123456/'
        }))

        expect(
            TRRFormatter().doc_format(doc)
        ).to.eq({
            'id': '123456',
            'to': '/trr/123456/'
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

        result = LawsuitFormatter().serialize([LawsuitDocType(_id=lawsuit_2.id), LawsuitDocType(_id=lawsuit_1.id)])
        expected_result = [
            {
                'id': lawsuit_2.id,
                'case_no': '00-L-5231',
                'primary_cause': 'FALSE ARREST',
                'to': '/lawsuit/00-L-5231/',
                'summary': 'Lawsuit Summary 2',
            },
            {
                'id': lawsuit_1.id,
                'case_no': '00-L-5230',
                'primary_cause': 'ILLEGAL SEARCH/SEIZURE',
                'to': '/lawsuit/00-L-5230/',
                'summary': 'Lawsuit Summary 1',
                'incident_date': '2002-01-03'
            }
        ]
        expect(result).to.eq(expected_result)


class AreaFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'name': 'name',
            'type': 'community',
        }))
        expect(AreaFormatter().doc_format(doc)).to.eq({
            'name': 'name',
            'type': 'community',
        })


class RankFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'rank': 'Police Officer',
            'active_officers_count': 1,
            'officers_most_complaints': ['Raymond', 'Jason']
        }))
        expect(RankFormatter().doc_format(doc)).to.eq({
            'name': 'Police Officer',
            'active_officers_count': 1,
            'officers_most_complaints': ['Raymond', 'Jason']
        })


class ZipCodeFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'zip_code': '666666',
            'url': 'cpdp.com'
        }))
        expect(ZipCodeFormatter().doc_format(doc)).to.eq({
            'name': '666666',
            'url': 'cpdp.com'
        })


class SearchTermFormatterTestCase(SimpleTestCase):
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'slug': 'communities',
            'name': 'Communities',
            'category_name': 'Geography',
            'description': 'Community description',
            'call_to_action_type': 'view_all',
            'link': '/url-mediator/session-builder/?community=123456',
        }))

        expect(SearchTermFormatter().doc_format(doc)).to.be.eq({
            'id': 'communities',
            'name': 'Communities',
            'category_name': 'Geography',
            'description': 'Community description',
            'call_to_action_type': 'view_all',
            'link': 'http://cpdb.lvh.me/url-mediator/session-builder/?community=123456'
        })

    def test_doc_format_empty_link(self):
        doc = Mock(to_dict=Mock(return_value={
            'slug': 'communities',
            'name': 'Communities',
            'category_name': 'Geography',
            'description': 'Community description',
            'call_to_action_type': 'view_all',
        }))

        expect(SearchTermFormatter().doc_format(doc)).to.be.eq({
            'id': 'communities',
            'name': 'Communities',
            'category_name': 'Geography',
            'description': 'Community description',
            'call_to_action_type': 'view_all',
            'link': ''
        })
