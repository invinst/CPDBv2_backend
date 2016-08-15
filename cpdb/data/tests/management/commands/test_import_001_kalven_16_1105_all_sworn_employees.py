from datetime import date

from django.test.testcases import TestCase
from django.core import management

from data.models import Officer, OfficerHistory, OfficerBadgeNumber, PoliceUnit


class ImportSwornOfficerDataTestCase(TestCase):
    def assert_data(self, model, expect_data):
        self.assertListEqual(sorted(
            list(model.objects.values(*expect_data[0].keys())),
            key=lambda datum: datum['pk']), expect_data)

    def test_import_sworn_officer_data(self):
        management.call_command(
            'import_001_kalven_16_1105_all_sworn_employees',
            file='cpdb/data/tests/management/commands/test_data/test_kalven_sworn_employees.csv')

        self.assert_data(Officer, [{
            'pk': 1,
            'full_name': 'Bb Aa',
            'gender': 'M',
            'race': 'WHITE',
            'appointed_date': date(2001, 1, 1),
            'age_at_march_11_2016': 55
        }, {
            'pk': 2,
            'full_name': 'Dd Cc',
            'gender': 'F',
            'race': 'BLACK',
            'appointed_date': date(2002, 2, 2),
            'age_at_march_11_2016': 44
        }])

        self.assert_data(PoliceUnit, [{
            'pk': 1,
            'unit_name': '001'
            }, {
            'pk': 2,
            'unit_name': '002'
            }, {
            'pk': 3,
            'unit_name': '003'
            }])

        self.assert_data(OfficerHistory, [{
            'pk': 1,
            'officer': 1,
            'unit': 1,
            'effective_date': date(2001, 1, 2),
            'end_date': date(2011, 11, 11)
            }, {
            'pk': 2,
            'officer': 1,
            'unit': 2,
            'effective_date': date(2012, 1, 1),
            'end_date': date(2012, 11, 12)
            }, {
            'pk': 3,
            'officer': 2,
            'unit': 3,
            'effective_date': date(2002, 2, 3),
            'end_date': date(2012, 12, 12)
            }])

        self.assert_data(OfficerBadgeNumber, [{
            'pk': 1,
            'star': '11101',
            'current': False
            }, {
            'pk': 2,
            'star': '11111',
            'current': False
            }, {
            'pk': 3,
            'star': '12201',
            'current': False
            }, {
            'pk': 4,
            'star': '12202',
            'current': False
            }])
