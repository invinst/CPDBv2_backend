from datetime import datetime

from django.test import SimpleTestCase

from robber import expect

from search.date_util import find_dates_from_string


class DateUtilTestCase(SimpleTestCase):
    def test_find_dates_from_string_single_date(self):
        test_cases = {
            '2018-06-01': [datetime(2018, 6, 1)],
            '1 Jun 2018': [datetime(2018, 6, 1)],
            '1 June 2018': [datetime(2018, 6, 1)],

            'June 1st 2018': [datetime(2018, 6, 1)],
            'June 2nd 2018': [datetime(2018, 6, 2)],
            'June 3rd 2018': [datetime(2018, 6, 3)],
            'June 4th 2018': [datetime(2018, 6, 4)],

            'June 1, 2018': [datetime(2018, 6, 1)],
            '6/1/18': [datetime(2018, 6, 1)],
            '06/01/2018': [datetime(2018, 6, 1)],

            'Jan 1, 2018': [datetime(2018, 1, 1)],
            'Feb 1, 2018': [datetime(2018, 2, 1)],
            'Mar 1, 2018': [datetime(2018, 3, 1)],
            'Apr 1, 2018': [datetime(2018, 4, 1)],
            'May 1, 2018': [datetime(2018, 5, 1)],
            'Jun 1, 2018': [datetime(2018, 6, 1)],
            'Jul 1, 2018': [datetime(2018, 7, 1)],
            'Aug 1, 2018': [datetime(2018, 8, 1)],
            'Sep 1, 2018': [datetime(2018, 9, 1)],
            'Oct 1, 2018': [datetime(2018, 10, 1)],
            'Nov 1, 2018': [datetime(2018, 11, 1)],
            'Dec 1, 2018': [datetime(2018, 12, 1)],

            'January 2, 2018': [datetime(2018, 1, 2)],
            'February 2, 2018': [datetime(2018, 2, 2)],
            'March 2, 2018': [datetime(2018, 3, 2)],
            'April 2, 2018': [datetime(2018, 4, 2)],
            'May 2, 2018': [datetime(2018, 5, 2)],
            'June 2, 2018': [datetime(2018, 6, 2)],
            'July 2, 2018': [datetime(2018, 7, 2)],
            'August 2, 2018': [datetime(2018, 8, 2)],
            'September 2, 2018': [datetime(2018, 9, 2)],
            'October 2, 2018': [datetime(2018, 10, 2)],
            'November 2, 2018': [datetime(2018, 11, 2)],
            'December 2, 2018': [datetime(2018, 12, 2)],

            '2001-01-01 1223123': [datetime(2001, 1, 1)],
            '2001-01-01 1223': [datetime(2001, 1, 1)],
            '2004 2001-01-01': [datetime(2001, 1, 1)],
            'ke 2001-01-01': [datetime(2001, 1, 1)],
            '2001-01-01 j an 1': [datetime(2001, 1, 1)],
            '2001 Jan 12 j an 1': [datetime(2001, 1, 12)],
            '2001 february 12 j an 1': [datetime(2001, 2, 12)],
            '2004 2001 feb 12 j an 1': [datetime(2001, 2, 12)]
        }

        for string, dates in test_cases.iteritems():
            expect(find_dates_from_string(string)).to.eq(dates)

    def test_find_dates_from_string_multiple_dates(self):
        test_cases = {
            '2001 Jan 12 2014 Oct 1st ': [datetime(2001, 1, 12), datetime(2014, 10, 1)],
            '2001-01-01 2004 02  01  ke': [datetime(2001, 1, 1), datetime(2004, 2, 1)],
            '2004 2001-01-01 2014 Jan 12': [datetime(2001, 1, 1), datetime(2014, 1, 12)],
            '2001-01-01 de 2014 Jan 12': [datetime(2001, 1, 1), datetime(2014, 1, 12)],
        }

        for string, dates in test_cases.iteritems():
            expect(find_dates_from_string(string)).to.eq(dates)

    def test_find_dates_from_string_invalid_dates(self):
        invalid_date_strings = [
            '2000-2-30',
            '2001-2-29',
            '2001-4-31',
            '2001-2--29',
        ]
        for invalid_date_string in invalid_date_strings:
            expect(find_dates_from_string(invalid_date_string)).to.eq([])

    def test_find_dates_from_string_incomplete_dates(self):
        incomplete_date_strings = [
            '2000-2',
            '2001-29',
            '2001 Jun',
            'June 2001',
            'Jun 1st',
            'June 1st',
            '1st June',
        ]
        for incomplete_date_string in incomplete_date_strings:
            expect(find_dates_from_string(incomplete_date_string)).to.eq([])
