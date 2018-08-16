from django.test import SimpleTestCase

from mock import patch
from robber import expect

from search.utils import chicago_zip_codes


class UtilsTestCase(SimpleTestCase):
    @patch('search.utils.zipcodes.filter_by')
    @patch('search.utils.zipcodes.list_all')
    def test_chicago_zip_codes(self, list_all_mock, filter_by_mock):
        list_all_mock.return_value = [{
            'active': True,
            'zip_code': '123456',
            'country': 'US',
            'city': 'CHICAGO'
        }, {
            'active': True,
            'zip_code': '666666',
            'country': 'US',
            'city': 'FRANKLIN'
        }]
        filter_by_mock.return_value = [{
            'zip_code': '123456',
            'country': 'US',
            'city': 'CHICAGO'
        }]
        zip_codes = chicago_zip_codes()

        expect(list_all_mock).to.be.called_once()
        expect(filter_by_mock).to.be.called_once_with(list_all_mock(), active=True, city='CHICAGO')

        expect(zip_codes).to.have.length(1)
        expect(zip_codes[0].pk).to.eq(0)
        expect(zip_codes[0].zip_code).to.eq('123456')
        expect(zip_codes[0].to).to.eq('https://google.com.vn')
