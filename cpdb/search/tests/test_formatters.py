from mock import Mock

from django.test import SimpleTestCase

from robber import expect

from search.formatters import (
    SimpleFormatter, OfficerFormatter, OfficerV2Formatter,
    NameV2Formatter, ReportFormatter, Formatter, UnitFormatter, CRFormatter, TRRFormatter,
    AreaFormatter, RankFormatter)


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

    def test_serialize(self):
        doc = Mock(
            to_dict=Mock(return_value={'a': 'a'}),
            _id='a_id'
        )
        expect(SimpleFormatter().serialize([doc])).to.eq([{
            'a': 'a',
            'id': 'a_id'
        }])


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
            'trr_count': 1,
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
            'percentiles': [],
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
    def test_doc_format(self):
        doc = Mock(to_dict=Mock(return_value={
            'crid': '123456',
            'to': '/complaint/123456/'
        }))

        expect(
            CRFormatter().doc_format(doc)
        ).to.eq({
            'crid': '123456',
            'to': '/complaint/123456/'
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
            'rank': 'Police Officer'
        }))
        expect(RankFormatter().doc_format(doc)).to.eq({
            'name': 'Police Officer'
        })
