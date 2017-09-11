from datetime import datetime, date

import numpy as np
import pytz
from django.test import SimpleTestCase
from freezegun import freeze_time
from pandas import DataFrame
from robber import expect

from data_importer.base.cleaner import DataCleaner, ToBool, ToNaN, ToDateTime, ToDate, ZFill, Just, strip, \
    capitalise_generation_suffix, clean_name, titleize, to_int, ignore_null, lower


class DataCleanerTestCase(SimpleTestCase):
    def test_perform(self):
        df = DataFrame([{'key': 'AARON ', 'int': '1970.0'}])
        schema = {
            'key': [str, str.strip, str.title],
            'int': [float, int],
        }
        df_cleaned = DataCleaner(schema).perform(df)
        expect(df_cleaned.equals(DataFrame([{'key': 'Aaron', 'int': 1970}]))).to.be.true()

    def test_perform_nan_field(self):
        df = DataFrame([{'none': np.nan}])
        schema = {
            'none': [str, float]
        }
        df_cleaned = DataCleaner(schema).perform(df)
        expect(df_cleaned.equals(DataFrame([{'none': np.nan}]))).to.be.true()


class ToBoolTestCase(SimpleTestCase):
    def test_call(self):
        to_bool = ToBool(true_set=['ON', 'Y', '\xce\xa5'], false_set=['OFF', 'N', '\xce\x9d'])

        expect(lambda: to_bool('')).to.throw(Exception)
        expect(to_bool('ON')).to.be.eq(True)
        expect(to_bool('Y')).to.be.eq(True)
        expect(to_bool('\xce\xa5')).to.be.eq(True)
        expect(to_bool('OFF')).to.be.eq(False)
        expect(to_bool('N')).to.be.eq(False)
        expect(to_bool('\xce\x9d')).to.be.eq(False)
        expect(lambda: to_bool('No')).to.throw(Exception)


class ToNaNTestCase(SimpleTestCase):
    def test_call(self):
        to_nan = ToNaN(value_set=[''])
        expect(bool(np.isnan(to_nan('')))).to.be.true()
        expect(to_nan('abc')).to.be.eq('abc')
        expect(to_nan(1)).to.be.eq(1)


class ToDateTimeTestCase(SimpleTestCase):
    @freeze_time('2017-07-21 12:00:01', ignore=['py.test'])
    def test_call(self):
        timezone = 'America/Chicago'
        expected = pytz.timezone(timezone).localize(datetime(year=2001, day=30, month=1))

        expect(ToDateTime(patterns=['%d-%b-%y'], timezone=timezone)('30-Jan-01')).to.be.eq(expected)
        expect(lambda: ToDateTime(patterns=[])('30-Jan-01')).to.throw(Exception)

    @freeze_time('2017-07-21 12:00:01', ignore=['py.test'])
    def test_call_with_null(self):
        timezone = 'America/Chicago'
        expect(ToDateTime(patterns=['%d-%b-%y'], timezone=timezone)(None)).to.be.eq(None)

    @freeze_time('2017-07-21 12:00:01', ignore=['py.test'])
    def test_call_19th_century(self):
        timezone = 'America/Chicago'
        expected = pytz.timezone(timezone).localize(datetime(year=1920, day=30, month=1))

        expect(ToDateTime(patterns=['%d-%b-%y'], timezone=timezone)('30-Jan-20')).to.be.eq(expected)
        expect(lambda: ToDateTime(patterns=[])('30-Jan-01')).to.throw(Exception)


class ToDateTestCase(SimpleTestCase):
    def test_call(self):
        expect(ToDate(patterns=['%d-%m-%y', '%d-%b-%y'])('30-Jan-01')).to.be.eq(
            date(day=30, month=1, year=2001)
        )
        expect(ToDate(patterns=[])(None)).to.be.none()
        expect(lambda: ToDate(patterns=[])('30-Jan-01')).to.be.throw(Exception)


class ZFillTestCase(SimpleTestCase):
    def test_call(self):
        expect(ZFill(3)(1)).to.be.eq('001')
        expect(ZFill(3)(None)).to.be.eq(None)


class JustTestCase(SimpleTestCase):
    def test_call(self):
        expect(Just('this')('anything')).to.be.eq('this')


class StripTestCase(SimpleTestCase):
    def test_call(self):
        expect(strip('abc  ')).to.be.eq('abc')
        expect(strip(None)).to.be.none()


class TitleizeTestCase(SimpleTestCase):
    def test_call(self):
        expect(titleize('abc xyz')).to.be.eq('Abc Xyz')
        expect(titleize(None)).to.be.none()


class CapitaliseGenerationSuffixTestCase(SimpleTestCase):
    def test_call(self):
        expect(capitalise_generation_suffix('Jarvan iv')).to.be.eq('Jarvan IV')


class CleanNameTestCase(SimpleTestCase):
    def test_call(self):
        expect(clean_name('C 0    Reilly Ii')).to.be.eq('C. O\'Reilly II')
        expect(clean_name('C 0    Reilly sr')).to.be.eq('C. O\'Reilly Sr.')


class ToIntTestCase(SimpleTestCase):
    def test_call(self):
        expect(to_int(None)).to.be.none()
        expect(to_int('1.0')).to.be.eq(1)


class IgnoreNullTestCase(SimpleTestCase):
    def test_ignore_null(self):
        def foo(value):
            return value - 1

        expect(ignore_null(foo)(None)).to.be.eq(None)
        expect(ignore_null(foo)(2)).to.be.eq(1)


class LowerTestCase(SimpleTestCase):
    def test_call(self):
        expect(lower(None)).to.be.none()
        expect(lower('Foo')).to.be.eq('foo')
