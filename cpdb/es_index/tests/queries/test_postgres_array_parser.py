from decimal import Decimal
from datetime import datetime

from django.test import SimpleTestCase

from robber import expect

from es_index.queries.postgres_array_parser import parse_postgres_row_array


class PostgresArrayParserTestCase(SimpleTestCase):
    def test_number(self):
        expect(parse_postgres_row_array('{"(20)"}')).to.eq([(20,)])
        expect(parse_postgres_row_array('{"(2.3,)"}')).to.eq([(float('2.3'), None)])
        expect(parse_postgres_row_array('{"(1,)"}')).to.eq([(1, None)])
        expect(parse_postgres_row_array('{"(,1.3)"}')).to.eq([(None, float('1.3'))])

    def test_string(self):
        expect(parse_postgres_row_array('{"(abcdef)"}')).to.eq([('abcdef',)])
        expect(parse_postgres_row_array(
            '{"(https://www.documentcloud.org/documents/4332682-CRID-1046046_CR.html?test=%1&more=2)"}'
        )).to.eq([('https://www.documentcloud.org/documents/4332682-CRID-1046046_CR.html?test=%1&more=2',)])
        expect(parse_postgres_row_array('{"(1,abc-def)"}')).to.eq([(1, 'abc-def')])
        expect(parse_postgres_row_array('{"(abc-def,1)"}')).to.eq([('abc-def', 1)])
        expect(parse_postgres_row_array('{"(2,abc-def,1)"}')).to.eq([(2, 'abc-def', 1)])

    def test_quoted_string(self):
        expect(parse_postgres_row_array('{"(\\"Police Officer\\")"}')).to.eq([('Police Officer',)])
        expect(parse_postgres_row_array('{"(\\"Police Officer\\",)"}')).to.eq([('Police Officer', None)])
        expect(parse_postgres_row_array('{"(\\"123\\")"}')).to.eq([('123',)])
        expect(
            parse_postgres_row_array('{"(\\"{\\"\\"documentcloud_id\\"\\": \\"\\"4335853\\"\\"}\\")"}')
        ).to.eq([('{\\"\\"documentcloud_id\\"\\": \\"\\"4335853\\"\\"}',)])

    def test_datetime(self):
        expect(parse_postgres_row_array('{"(2016-03-05)"}')).to.eq([(datetime(2016, 3, 5),)])
        expect(parse_postgres_row_array('{"(2016-03-05,)"}')).to.eq([(datetime(2016, 3, 5), None)])
        expect(parse_postgres_row_array('{"(,2016-03-05)"}')).to.eq([(None, datetime(2016, 3, 5))])
        expect(
            parse_postgres_row_array('{"(1,2016-03-05,\\"Police-Officer\\")"}')
        ).to.eq([(1, datetime(2016, 3, 5), 'Police-Officer')])

    def test_boolean(self):
        expect(parse_postgres_row_array('{"(t)"}')).to.eq([(True,)])
        expect(parse_postgres_row_array('{"(f)"}')).to.eq([(False,)])
        expect(parse_postgres_row_array('{"(t,)"}')).to.eq([(True, None)])
        expect(parse_postgres_row_array('{"(f,)"}')).to.eq([(False, None)])
        expect(parse_postgres_row_array('{"(\\"t\\")"}')).to.eq([('t',)])
        expect(parse_postgres_row_array('{"(\\"f\\")"}')).to.eq([('f',)])

    def test_multiple_rows(self):
        expect(parse_postgres_row_array('{"(1,Captain)","(2,Officer)"}')).to.eq([(1, 'Captain'), (2, 'Officer')])

    def test_empty_json(self):
        expect(parse_postgres_row_array('{"({})"}')).to.eq([('{}',)])

    def test_skip_empty_row(self):
        expect(parse_postgres_row_array('{"(,,,)"}')).to.eq([])
