from django.test import SimpleTestCase

from robber import expect

from es_index.queries.postgres_array_parser import parse_postgres_row_array


class PostgresArrayParserTestCase(SimpleTestCase):
    def test_string(self):
        expect(parse_postgres_row_array('{"(abcdef)"}')).to.eq([('abcdef',)])
        expect(parse_postgres_row_array(
            '{"(https://www.documentcloud.org/documents/4332682-CRID-1046046_CR.html?test=%1&more=2)"}'
        )).to.eq([('https://www.documentcloud.org/documents/4332682-CRID-1046046_CR.html?test=%1&more=2',)])
        expect(parse_postgres_row_array('{"(1,abc-def)"}')).to.eq([('1', 'abc-def')])
        expect(parse_postgres_row_array('{"(abc-def,1)"}')).to.eq([('abc-def', '1')])
        expect(parse_postgres_row_array('{"(2,abc-def,1)"}')).to.eq([('2', 'abc-def', '1')])
        expect(parse_postgres_row_array('{"(002)"}')).to.eq([('002',)])

    def test_quoted_string(self):
        expect(parse_postgres_row_array('{"(\\"Police Officer\\")"}')).to.eq([('Police Officer',)])
        expect(parse_postgres_row_array('{"(\\"Police Officer\\",)"}')).to.eq([('Police Officer', None)])
        expect(parse_postgres_row_array('{"(\\"123\\")"}')).to.eq([('123',)])
        expect(
            parse_postgres_row_array('{"(\\"{\\"\\"documentcloud_id\\"\\": \\"\\"4335853\\"\\"}\\")"}')
        ).to.eq([('{"documentcloud_id": "4335853"}',)])
        expect(parse_postgres_row_array(
            '{"(\\"\\"\\"{\\\\\\\\\\"\\"normalized_title\\\\\\\\\\"\\": \\\\\\\\\\"\\"cr-271494\\\\\\\\\\"\\", '
            '\\\\\\\\\\"\\"documentcloud_id\\\\\\\\\\"\\": 1273462}\\"\\"\\")"}'
        )).to.eq([('{"normalized_title": "cr-271494", "documentcloud_id": 1273462}',)])

    def test_multiple_rows(self):
        expect(parse_postgres_row_array('{"(1,Captain)","(2,Officer)"}')).to.eq([('1', 'Captain'), ('2', 'Officer')])

    def test_empty_json(self):
        expect(parse_postgres_row_array('{"({})"}')).to.eq([('{}',)])

    def test_skip_empty_row(self):
        expect(parse_postgres_row_array('{"(,,,)"}')).to.eq([])
