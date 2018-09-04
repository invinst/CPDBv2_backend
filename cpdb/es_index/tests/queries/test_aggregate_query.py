from django.test import TestCase

from robber import expect

from es_index.queries.aggregate_query import AggregateQuery
from es_index.queries.distinct_query import DistinctQuery
from es_index.queries.subquery import Subquery
from es_index.queries.query_fields import RowArrayQueryField
from data.models import (
    PoliceWitness, Allegation, Officer, OfficerAllegation
)
from data.factories import (
    PoliceWitnessFactory, AllegationFactory, OfficerAllegationFactory
)


class AggregateQueryTestCase(TestCase):
    def setUp(self):
        class PoliceWitnessQuery(DistinctQuery):
            base_table = PoliceWitness
            joins = {
                'officer': Officer
            }
            fields = {
                'officer_id': 'officer_id',
                'allegation_id': 'allegation_id',
                'first_name': 'officer.first_name',
            }

        class AllegationQuery(AggregateQuery):
            base_table = Allegation
            joins = {
                'witnesses': Subquery(PoliceWitnessQuery(), on='allegation_id')
            }
            fields = {
                'id': 'id',
                'crid': 'crid',
                'witnesses': RowArrayQueryField('witnesses')
            }

        class ComplaintQuery(DistinctQuery):
            base_table = OfficerAllegation
            joins = {
                'allegation': Subquery(AllegationQuery(), on='id', left_on='allegation_id')
            }
            fields = {
                'crid': 'allegation.crid',
            }

        self.query = AllegationQuery()
        self.complaint_query = ComplaintQuery()

    def test_query_row_array(self):
        allegation = AllegationFactory(crid='123456', id=334455)
        PoliceWitnessFactory(
            officer__id=554433, officer__first_name='James', allegation=allegation)
        rows = list(self.query.execute())
        expect(rows).to.eq([
            {
                'id': 334455,
                'crid': '123456',
                'witnesses': [{
                    'officer_id': 554433,
                    'allegation_id': 334455,
                    'first_name': 'James'
                }]
            }
        ])

    def test_query_where_in(self):
        AllegationFactory()
        AllegationFactory(crid='123456')
        AllegationFactory(crid='654321')
        rows = list(self.query.where(crid__in=['654321', '123456']).execute())
        expect(set([row['crid'] for row in rows])).to.eq(set(['654321', '123456']))

    def test_query_where_in_number(self):
        AllegationFactory()
        AllegationFactory(id=1212)
        AllegationFactory(id=3434)
        rows = list(self.query.where(id__in=[1212, 3434]).execute())
        expect(set([row['id'] for row in rows])).to.eq(set([1212, 3434]))

    def test_query_where_equal(self):
        AllegationFactory()
        AllegationFactory(crid='123456')
        rows = list(self.query.where(crid='123456').execute())
        expect([row['crid'] for row in rows]).to.eq(['123456'])

    def test_query_left_on_join(self):
        allegation = AllegationFactory(crid='112233')
        OfficerAllegationFactory(allegation=allegation)
        rows = list(self.complaint_query.execute())
        expect(rows).to.eq([{'crid': '112233'}])
