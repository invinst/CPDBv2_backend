from django.test import TestCase
from robber import expect

from data.factories import OfficerFactory, PoliceUnitFactory
from data.models import OfficerHistory
from data_importer.base.utils.import_officer_history_helpers import create_officer_history, import_officer_history


class ImportOfficerHistoryHelpersTestCase(TestCase):
    def setUp(self):
        officer = OfficerFactory()
        unit = PoliceUnitFactory()

        self.officer = officer
        self.unit = unit

    def test_create_officer_history(self):
        create_officer_history(self.officer, self.unit, None, None)
        expect(OfficerHistory.objects.count()).to.be.eq(1)

    def test_import_officer_history_1(self):
        row1 = {
            'officer_id': self.officer.id, 'unit': self.unit, 'start_date': None, 'end_date': '2016-06-05'
        }

        row2 = {
            'officer_id': self.officer.id, 'unit': self.unit, 'start_date': '2015-01-01', 'end_date': None
        }

        row3 = {
            'officer_id': self.officer.id, 'unit': self.unit, 'start_date': None, 'end_date': None
        }

        for row in [row1, row2, row3]:
            import_officer_history(row)

        history = OfficerHistory.objects.first()

        expect(OfficerHistory.objects.count()).to.be.eq(1)
        expect(history.officer).to.be.eq(self.officer)
        expect(history.unit).to.be.eq(self.unit)
        expect(str(history.effective_date)).to.be.eq('2015-01-01')
        expect(str(history.end_date)).to.be.eq('2016-06-05')

    def test_import_officer_history_2(self):
        row1 = {
            'officer_id': self.officer.id, 'unit': self.unit, 'start_date': None, 'end_date': '2016-06-05'
        }

        row2 = {
            'officer_id': self.officer.id, 'unit': self.unit, 'start_date': '2015-01-01', 'end_date': '2015-02-02'
        }

        row3 = {
            'officer_id': self.officer.id, 'unit': self.unit, 'start_date': None, 'end_date': None
        }

        for row in [row1, row2, row3]:
            import_officer_history(row)

        expect(OfficerHistory.objects.count()).to.be.eq(2)

    def test_import_officer_history_3(self):
        row1 = {
            'officer_id': self.officer.id, 'unit': self.unit, 'start_date': None, 'end_date': '2016-06-05'
        }

        row2 = {
            'officer_id': self.officer.id, 'unit': self.unit, 'start_date': '2017-01-01', 'end_date': None
        }

        row3 = {
            'officer_id': self.officer.id, 'unit': self.unit, 'start_date': None, 'end_date': None
        }

        for row in [row1, row2, row3]:
            import_officer_history(row)

        expect(OfficerHistory.objects.count()).to.be.eq(2)
