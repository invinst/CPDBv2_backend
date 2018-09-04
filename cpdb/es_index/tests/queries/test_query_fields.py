from datetime import date

from django.test import SimpleTestCase
from django.contrib.gis.geos import Point

from robber import expect

from es_index.queries.query_fields import (
    GeometryQueryField, QueryField, CountQueryField, ForeignQueryField, RowArrayQueryField
)
from es_index.queries.distinct_query import DistinctQuery
from es_index.queries.subquery import Subquery
from es_index.queries.table import Table
from data.models import OfficerAllegation, Allegation, Officer, InvestigatorAllegation


class QueryFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.query_field_a = QueryField('officer.first_name')
        self.query_field_a.initialize(
            table_alias='my_table',
            table=Allegation,
            alias='my_first_name',
            joins={'officer': Officer}
        )

        self.query_field_b = QueryField('crid')
        self.query_field_b.initialize(
            table_alias='my_table',
            table=Allegation,
            alias='my_crid',
            joins={'officer': Officer}
        )

    def test_render(self):
        expect(self.query_field_a.render()).to.eq('officer.first_name AS my_first_name')
        expect(self.query_field_b.render()).to.eq('my_table.crid AS my_crid')

    def test_belong_to(self):
        expect(self.query_field_a.belong_to('my_table')).to.be.false()
        expect(self.query_field_a.belong_to('officer')).to.be.true()
        expect(self.query_field_b.belong_to('my_table')).to.be.true()

    def test_name_to_group(self):
        expect(self.query_field_a.name_to_group()).to.eq('officer.first_name')
        expect(self.query_field_b.name_to_group()).to.eq('my_table.crid')

    def test_alias(self):
        expect(self.query_field_a.alias()).to.eq('my_first_name')
        expect(self.query_field_b.alias()).to.eq('my_crid')

    def test_serialize(self):
        expect(self.query_field_a.serialize('abc')).to.eq('abc')
        expect(self.query_field_b.serialize(123)).to.eq(123)

    def test_kind(self):
        expect(self.query_field_a.kind).to.eq('varchar')
        expect(self.query_field_b.kind).to.eq('varchar')


class GeometryQueryFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.query_field = GeometryQueryField('point')
        self.query_field.initialize(
            table_alias='my_table',
            table=Allegation,
            alias='my_point',
            joins={}
        )

    def test_render(self):
        expect(self.query_field.render()).to.eq('ST_AsGML(my_table.point) AS my_point')

    def test_belong_to(self):
        expect(self.query_field.belong_to('my_table')).to.be.true()
        expect(self.query_field.belong_to('xyz')).to.be.false()

    def test_name_to_group(self):
        expect(self.query_field.name_to_group()).to.eq('my_table.point')

    def test_alias(self):
        expect(self.query_field.alias()).to.eq('my_point')

    def test_serialize(self):
        expect(str(self.query_field.serialize(
            '<gml:Point srsName="EPSG:4326"><gml:coordinates>'
            '-87.721100300000003,41.8372636</gml:coordinates></gml:Point>'
        ))).to.eq(str(Point(x=-87.7211003, y=41.8372636)))

    def test_serialize_with_none(self):
        expect(self.query_field.serialize(None)).to.be.none()


class CountQueryFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.query_field = CountQueryField(
            from_table=OfficerAllegation, related_to='officer'
        )
        self.query_field.initialize(
            table_alias='allegation',
            table=Allegation,
            alias='allegation_count',
            joins={'officer': Officer}
        )

    def test_render(self):
        expect(self.query_field.render()).to.eq(
            '( SELECT COUNT(*) FROM data_officerallegation WHERE officer_id = officer.id ) AS allegation_count'
        )

    def test_render_where(self):
        query_field = CountQueryField(
            from_table=Table(OfficerAllegation), related_to='officer', where={'final_finding': 'SU'}
        )
        query_field.initialize(
            table_alias='allegation',
            table=Allegation,
            alias='sustained_count',
            joins={'officer': Officer}
        )
        expect(query_field.render()).to.eq(
            '( SELECT COUNT(*) FROM data_officerallegation WHERE '
            'officer_id = officer.id AND final_finding = \'SU\' ) AS sustained_count'
        )

    def test_render_join_base_table(self):
        query_field = CountQueryField(
            from_table=InvestigatorAllegation, related_to='base_table'
        )
        query_field.initialize(
            table_alias='base_table',
            table=Allegation,
            alias='num_cases',
            joins={}
        )
        expect(query_field.render()).to.eq(
            '( SELECT COUNT(*) FROM data_investigatorallegation WHERE '
            'allegation_id = base_table.id ) AS num_cases'
        )

    def test_belong_to(self):
        expect(self.query_field.belong_to('allegation')).to.be.false()

    def test_name_to_group(self):
        expect(self.query_field.name_to_group()).to.eq('officer.id')

    def test_alias(self):
        expect(self.query_field.alias()).to.eq('allegation_count')

    def test_serialize(self):
        expect(self.query_field.serialize(10)).to.eq(10)


class ForeignQueryFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.query_field = ForeignQueryField(relation='beat_id', field_name='name')
        self.query_field.initialize(
            table_alias='allegation',
            table=Allegation,
            alias='beat_name',
            joins={}
        )

    def test_render(self):
        expect(self.query_field.render()).to.eq(
            '( SELECT name FROM data_area WHERE id = allegation.beat_id ) AS beat_name'
        )

    def test_belong_to(self):
        expect(self.query_field.belong_to('allegation')).to.be.false()

    def test_name_to_group(self):
        expect(self.query_field.name_to_group()).to.eq('allegation.beat_id')

    def test_alias(self):
        expect(self.query_field.alias()).to.eq('beat_name')

    def test_serialize(self):
        expect(self.query_field.serialize('abc')).to.eq('abc')


class RowArrayQueryFieldTestCase(SimpleTestCase):
    def setUp(self):
        class CoaccusedQuery(DistinctQuery):
            base_table = OfficerAllegation
            joins = {
                'officer': Officer
            }
            fields = {
                'id': 'officer.id',
                'final_finding': 'final_finding',
                'disciplined': 'disciplined',
                'start_date': 'start_date',
            }
        subquery = Subquery(CoaccusedQuery(), on='allegation_id')
        self.query_field = RowArrayQueryField('coaccused')
        self.query_field.initialize(
            table_alias='allegation',
            table=Allegation,
            alias='coaccused',
            joins={
                'coaccused': subquery,
            }
        )

    def test_render(self):
        expect(self.query_field.render()).to.eq(
            'array_agg(DISTINCT ROW( '
            'coaccused.disciplined, coaccused.start_date, coaccused.id, coaccused.final_finding )) '
            'AS coaccused'
        )

    def test_belong_to(self):
        expect(self.query_field.belong_to('allegation')).to.be.false()

    def test_name_to_group(self):
        expect(self.query_field.name_to_group()).to.be.none()

    def test_alias(self):
        expect(self.query_field.alias()).to.eq('coaccused')

    def test_serialize(self):
        expect(self.query_field.serialize(
            '{"(t,2000-01-01,1,SU)","(f,2001-01-01,2,NS)"}'
        )).to.eq([
            {
                'id': 1,
                'final_finding': 'SU',
                'disciplined': True,
                'start_date': date(2000, 1, 1),
            },
            {
                'id': 2,
                'final_finding': 'NS',
                'disciplined': False,
                'start_date': date(2001, 1, 1),
            }
        ])

    def test_serialize_subfield(self):
        test_case_with_expect = [
            ('smallint', '1', 1),
            ('varchar', 'abc', 'abc'),
            ('text', 'abc', 'abc'),
            ('numeric', '1.2', 1.2),
            ('boolean', 't', True),
            ('boolean', 'f', False),
            ('boolean', None, None),
            ('date', '2016-08-14', date(2016, 8, 14)),
            ('integer', '12', 12),
            ('serial', '12', 12),
            (None, 'abc', None),
            ('numeric', None, None),
            ('jsonb', '{\\"\\"key\\"\\":\\"\\"value\\"\\"}', {'key': 'value'})
        ]

        for kind, string, expectation in test_case_with_expect:
            expect(self.query_field.serialize_subfield(kind, string)).to.eq(expectation)

    def test_serialize_subfield_geometry_field(self):
        expect(self.query_field.serialize_subfield(
            'geometry',
            (
                '<gml:Point srsName="EPSG:4326"><gml:coordinates>'
                '-87.721100300000003,41.8372636</gml:coordinates></gml:Point>'
            )
        )).to.eq(str(Point(x=-87.7211003, y=41.8372636)))

    def test_serialize_subfield_not_support_kind(self):
        with self.assertRaisesRegexp(
                NotImplementedError, 'Cannot yet serialize subfield of kind "my_type", value was "my_string"'):
            self.query_field.serialize_subfield('my_type', 'my_string')
