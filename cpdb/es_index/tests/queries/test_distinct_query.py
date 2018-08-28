from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect

from es_index.queries.distinct_query import DistinctQuery
from es_index.queries.query_fields import (
    CountQueryField, GeometryQueryField, ForeignQueryField
)
from data.models import (
    OfficerAllegation, Officer, Allegation, InvestigatorAllegation
)
from data.factories import (
    OfficerAllegationFactory, AllegationFactory, OfficerFactory,
    InvestigatorAllegationFactory
)


class DistinctQueryTestCase(TestCase):
    def setUp(self):
        class OfficerAllegationQuery(DistinctQuery):
            base_table = OfficerAllegation
            joins = {
                'allegation': Allegation,
                'officer': Officer
            }
            fields = {
                'crid': 'allegation.crid',
                'final_finding': 'final_finding',
                'allegation_count': CountQueryField(
                    from_table=OfficerAllegation, related_to='officer'),
                'sustained_count': CountQueryField(
                    from_table=OfficerAllegation, related_to='officer', where={'final_finding': 'SU'}),
            }

        self.complaint_query = OfficerAllegationQuery()

        class AllegationQuery(DistinctQuery):
            base_table = Allegation
            fields = {
                'id': 'id',
                'crid': 'crid',
                'num_cases': CountQueryField(
                    from_table=InvestigatorAllegation, related_to='base_table'),
                'point': GeometryQueryField('point'),
                'beat': ForeignQueryField(relation='beat_id', field_name='name'),
            }

        self.incident_query = AllegationQuery()

    def test_query_own_field(self):
        OfficerAllegationFactory(final_finding='NS')
        rows = list(self.complaint_query.execute())
        expect(rows).to.have.length(1)
        expect(rows[0]['final_finding']).to.eq('NS')

    def test_query_join_field(self):
        allegation = AllegationFactory(crid='123456')
        OfficerAllegationFactory(allegation=allegation)
        rows = list(self.complaint_query.execute())
        expect(rows).to.have.length(1)
        expect(rows[0]['crid']).to.eq('123456')

    def test_query_count(self):
        officer = OfficerFactory()
        OfficerAllegationFactory.create_batch(2, final_finding='NS', officer=officer)
        OfficerAllegationFactory.create_batch(1, final_finding='SU', officer=officer)
        rows = list(self.complaint_query.execute())
        expect(rows[0]['allegation_count']).to.eq(3)
        expect(rows[0]['sustained_count']).to.eq(1)

    def test_query_count_base_table(self):
        allegation = AllegationFactory()
        InvestigatorAllegationFactory.create_batch(2, allegation=allegation)
        rows = list(self.incident_query.execute())
        expect(rows).to.have.length(1)
        expect(rows[0]['num_cases']).to.eq(2)

    def test_query_geometry_field(self):
        point = Point(x=10, y=11)
        AllegationFactory(point=point)
        rows = list(self.incident_query.execute())
        expect(rows).to.have.length(1)
        extracted_point = rows[0]['point']
        expect(extracted_point.x).to.eq(point.x)
        expect(extracted_point.y).to.eq(point.y)

    def test_query_where_in(self):
        AllegationFactory()
        AllegationFactory(crid='123456')
        AllegationFactory(crid='654321')
        rows = list(self.incident_query.where(crid__in=['654321', '123456']).execute())
        expect(set([row['crid'] for row in rows])).to.eq(set(['654321', '123456']))

    def test_query_where_in_number(self):
        AllegationFactory()
        AllegationFactory(id=1212)
        AllegationFactory(id=3434)
        rows = list(self.incident_query.where(id__in=[1212, 3434]).execute())
        expect(set([row['id'] for row in rows])).to.eq(set([1212, 3434]))

    def test_query_where_equal(self):
        AllegationFactory()
        AllegationFactory(crid='123456')
        rows = list(self.incident_query.where(crid='123456').execute())
        expect([row['crid'] for row in rows]).to.eq(['123456'])

    def test_query_non_existent_operator(self):
        with self.assertRaisesRegexp(
            NotImplementedError,
            'foobar lookup is not supported yet.'
        ):
            self.incident_query.where(crid__foobar=123).execute()

    def test_query_non_supported_value(self):
        with self.assertRaisesRegexp(
            NotImplementedError,
            'lookup value of type Foo is not supported yet.'
        ):
            class Foo(object):
                pass
            self.incident_query.where(crid=Foo()).execute()

    def test_query_where_in_empty_list(self):
        with self.assertRaisesRegexp(
            ValueError,
            'Cant do "in" lookup for empty list.'
        ):
            self.incident_query.where(id__in=[]).execute()
