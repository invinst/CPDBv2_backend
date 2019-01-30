from django.test import TestCase
from django.db import connection

from robber import expect

from data.factories import OfficerFactory
from utils.raw_query_utils import dict_fetch_all


class RawQueryUtilsTestCase(TestCase):
    def test_dict_fetch_all(self):
        OfficerFactory(first_name='Jerome', last_name='Finnigan')
        OfficerFactory(first_name='Edward', last_name='May')

        build_query = 'SELECT first_name, last_name FROM data_officer'
        cursor = connection.cursor()
        cursor.execute(build_query)

        expect(dict_fetch_all(cursor)).to.eq([
            {'first_name': 'Jerome', 'last_name': 'Finnigan'},
            {'first_name': 'Edward', 'last_name': 'May'}
        ])
