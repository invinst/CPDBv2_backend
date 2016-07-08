import datetime

import pytz
import iso8601

from django.core import management
from django.test.testcases import TestCase
from django.utils import timezone

from data.models import (
    PoliceUnit, Officer, OfficerBadgeNumber, OfficerHistory, Area, LineArea,
    Investigator, Allegation, AllegationCategory, OfficerAllegation, PoliceWitness,
    Complainant, OfficerAlias)


class ImportV1DataTestCase(TestCase):
    def assert_data(self, model, expect_data):
        self.assertListEqual(sorted(
            list(model.objects.values(*expect_data[0].keys())),
            key=lambda datum: datum['pk']), expect_data)

    def test_import_v1_data(self):
        management.call_command('import_v1_data', folder='cpdb/data/tests/management/command/v1_data')
        self.assert_data(PoliceUnit, [{
            'pk': 1,
            'unit_name': '014'
            },
            {
            'pk': 2,
            'unit_name': '015'
            }])

        self.assert_data(Officer, [{
            'pk': 1,
            'first_name': 'Mary',
            'last_name': 'Jeleniewski',
            'race': 'White',
            'gender': 'F',
            'appointed_date': datetime.date(1987, 3, 9),
            'unit': 1,
            'rank': '',
            'birth_year': 1950,
            'active': 'Unknown'
            },
            {
            'pk': 2,
            'first_name': 'Ginger',
            'last_name': 'Jones',
            'race': 'Black',
            'gender': 'M',
            'appointed_date': datetime.date(2007, 4, 2),
            'unit': 2,
            'rank': 'PO',
            'birth_year': 1979,
            'active': 'Yes'
            }])
        self.assert_data(OfficerBadgeNumber, [{
            'pk': 1,
            'officer': 1,
            'star': '111',
            'current': True
            },
            {
            'pk': 2,
            'officer': 2,
            'star': '222',
            'current': False
            }])

        self.assert_data(OfficerHistory, [{
            'pk': 1,
            'officer': 1,
            'unit': 1,
            'effective_date': datetime.date(2001, 1, 1),
            'end_date': datetime.date(2001, 1, 11)
            },
            {
            'pk': 2,
            'officer': 2,
            'unit': 2,
            'effective_date': datetime.date(2002, 2, 2),
            'end_date': datetime.date(2002, 2, 12)
            }])

        areas = Area.objects.all()
        self.assertEqual(areas[0].polygon.__str__(), (
            'SRID=4326;MULTIPOLYGON (((-87.0000000000000000 41.0000000000000000,'
            ' -86.0000000000000000 42.0000000000000000, -85.0000000000000000 43.0000000000000000,'
            ' -87.0000000000000000 41.0000000000000000)))'))
        self.assertEqual(areas[0].pk, 1)
        self.assertEqual(areas[0].name, 'Edgewater')
        self.assertEqual(areas[0].type, 'neighborhoods')
        self.assertEqual(areas[1].polygon.__str__(), (
            'SRID=4326;MULTIPOLYGON (((-87.0000000000000000 43.0000000000000000,'
            ' -86.0000000000000000 41.0000000000000000, -85.0000000000000000 42.0000000000000000,'
            ' -87.0000000000000000 43.0000000000000000)))'))
        self.assertEqual(areas[1].pk, 2)
        self.assertEqual(areas[1].name, '2532')
        self.assertEqual(areas[1].type, 'police-beats')

        lineareas = LineArea.objects.all()
        self.assertEqual(lineareas[0].pk, 1)
        self.assertEqual(lineareas[0].name, 'MCPHERSON')
        self.assertEqual(lineareas[0].type, 'passageway')
        self.assertEqual(lineareas[0].geom.__str__(), (
            'SRID=4326;MULTILINESTRING ((-87.6776441465162861 41.9669399158901868, '
            '-87.6761545193971585 41.9669615171530594, '
            '-87.6762051103621616 41.9687949583315145))'))
        self.assertEqual(lineareas[1].pk, 2)
        self.assertEqual(lineareas[1].name, 'CLARK HS')
        self.assertEqual(lineareas[1].type, 'passageway')
        self.assertEqual(lineareas[1].geom.__str__(), (
            'SRID=4326;MULTILINESTRING ((-87.7574153386844245 41.8729155545781566, '
            '-87.7548059804398974 41.8729463761624459), (-87.7548059804398974 41.8729463761624459, '
            '-87.7532812159638951 41.8729679678796742, -87.7533180288366026 41.8739640379105253), '
            '(-87.7548937674160783 41.8757540602825671, -87.7548593581159366 41.8748475492969661, '
            '-87.7548279397935431 41.8739451238801692, -87.7548059804398974 41.8729463761624459))'))

        self.assert_data(Investigator, [{
            'pk': 1,
            'raw_name': 'ADDINGTON, MARC',
            'name': 'Marc Addington',
            'current_rank': 'INVESTIGATOR I IPRA',
            'current_report': 'abc',
            'unit': None,
            'agency': 'IPRA'
            },
            {
            'pk': 2,
            'raw_name': 'ADDUCI, MARK',
            'name': 'Mark Adduci',
            'current_rank': '',
            'current_report': '',
            'unit': 2,
            'agency': 'IAD'
            }])

        self.assert_data(Allegation, [{
            'pk': 1,
            'crid': '1076375',
            'summary': '',
            'location': '17',
            'add1': 6000,
            'add2': 'S NAGLE AVE',
            'city': 'CHICAGO IL',
            'incident_date':
                iso8601.parse_date('2015-07-27 19:24:00')
                .replace(tzinfo=timezone.get_default_timezone()).astimezone(pytz.utc),
            'investigator': 1,
            'areas': 1,
            'line_areas': None,
            'point': None,
            'beat': 1,
            'source': ''
            }, {
            'pk': 2,
            'crid': '309230',
            'summary': '',
            'location': '',
            'add1': None,
            'add2': '',
            'city': '',
            'incident_date': None,
            'investigator': 1,
            'areas': 2,
            'line_areas': 1,
            'point': None,
            'beat': None,
            'source': 'moore'
            }])

        self.assert_data(AllegationCategory, [{
            'pk': 1,
            'cat_id': '029',
            'category': 'Operation/Personnel Violations',
            'allegation_name': 'Failure To Identify',
            'on_duty': True,
            'citizen_dept': 'dept'
            },
            {
            'pk': 2,
            'cat_id': '02A',
            'category': 'Drug / Alcohol Abuse',
            'allegation_name': 'Intoxicated On Duty',
            'on_duty': False,
            'citizen_dept': '?'
            }])

        self.assert_data(OfficerAllegation, [{
            'pk': 1,
            'allegation': 1,
            'cat': 1,
            'officer': 1,
            'start_date': None,
            'end_date': None,
            'officer_age': None,
            'recc_finding': '',
            'recc_outcome': '',
            'final_finding': 'UN',
            'final_outcome': '',
            'final_outcome_class': 'not-sustained'
            },
            {
            'pk': 2,
            'allegation': 2,
            'cat': None,
            'officer': 2,
            'start_date': datetime.date(2001, 1, 1),
            'end_date': datetime.date(2001, 1, 11),
            'officer_age': None,
            'recc_finding': '',
            'recc_outcome': '',
            'final_finding': 'NS',
            'final_outcome': '600',
            'final_outcome_class': 'not-sustained'
            }])

        self.assert_data(PoliceWitness, [{
            'pk': 1,
            'allegation': 1,
            'gender': 'M',
            'race': 'White',
            'officer': 1
            },
            {
            'pk': 2,
            'allegation': 2,
            'gender': 'F',
            'race': 'Black',
            'officer': 2
            }])

        self.assert_data(Complainant, [{
            'pk': 1,
            'allegation': 1,
            'gender': 'M',
            'race': 'White',
            'age': None
            },
            {
            'pk': 2,
            'allegation': 2,
            'gender': 'F',
            'race': 'Black',
            'age': 54
            }])

        self.assert_data(OfficerAlias, [{
            'pk': 1,
            'old_officer_id': 3,
            'new_officer': 1
            },
            {
            'pk': 2,
            'old_officer_id': 4,
            'new_officer': 2
            }])
