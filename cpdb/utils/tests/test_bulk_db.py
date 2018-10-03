from django.test.testcases import TestCase

from robber import expect

from utils.bulk_db import build_bulk_update_sql


class BulkDbTestCase(TestCase):
    def test_build_bulk_update_sql(self):
        def _format_sql(sql_string):
            ''.join(sql_string.replace('\n', '').split())

        batch_data = [
            {
                'id': 1,
                'first_name': 'Roman',
                'complaint_percentile': 50
            },
            {
                'id': 2,
                'first_name': 'Jerome',
                'complaint_percentile': 78
            }
        ]

        expected_sql_string = '''
            UPDATE officer AS t SET
              complaint_percentile = c.complaint_percentile
            FROM (values
              ((NULL::officer).id, (NULL::officer).first_name, (NULL::officer).complaint_percentile),
              (1, 'Roman', 50), (2, 'Jerome', 78)
            ) AS c(id, first_name, complaint_percentile)
            WHERE c.id = t.id;
        '''

        sql_string = build_bulk_update_sql('officer', 'id', ['first_name', 'complaint_percentile'], batch_data)
        expect(_format_sql(sql_string)).to.eq(_format_sql(expected_sql_string))
