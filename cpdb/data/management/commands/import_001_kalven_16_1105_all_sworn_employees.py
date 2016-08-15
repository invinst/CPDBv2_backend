import csv
from datetime import datetime

from django.core.management import BaseCommand
from tqdm import tqdm

from data.models import Officer, OfficerHistory, OfficerBadgeNumber, PoliceUnit
from data.utils.clean_name import clean_name
from data_versioning.changekeepers import PostgreSQLChangeKeeper


class Command(BaseCommand):
    change_keeper = PostgreSQLChangeKeeper()
    source = {
        'file': 'Kalven 16-1105 All Sworn Employees.xlsx',
        'production_date': 'March 11, 2016',
        'download_link': (
            'http://bd3d4f06ce9a37fff3a5-6c6a50368b2bddd83592ee0148675920.r76.cf5.'
            'rackcdn.com/Kalven%2016-1105%20All%20Sworn%20Employees%20(3).xlsx')
    }

    def add_arguments(self, parser):
        parser.add_argument('--file')

    def _clean_date(self, val):
        if val:
            return datetime.strptime(val, '%d-%b-%y')
        return None

    def _process_batch(self, batch):
        if not batch:
            return
        row = batch[0]
        officer = self._create_officer(row)
        self._insert_badge_number(row, officer)
        for row in batch:
            self._create_officer_history(row, officer)

    def _create_officer_history(self, row, officer):
        try:
            unit = PoliceUnit.objects.get(unit_name=row['CPD_UNIT_ASSIGNED_NO'])
        except PoliceUnit.DoesNotExist:
            unit = self.change_keeper.create(
                PoliceUnit, source=self.source,
                content={'unit_name': row['CPD_UNIT_ASSIGNED_NO']})

        self.change_keeper.create(
            OfficerHistory, source=self.source,
            content={
                'officer': officer,
                'unit': unit,
                'effective_date': self._clean_date(row['EFFECTIVE_DATE']),
                'end_date': self._clean_date(row['END_DATE'])
            })

    def _create_officer(self, row):
        full_name = clean_name('%s %s' % (row['FIRST_NME'], row['LAST_NME']))
        return self.change_keeper.create(
            Officer, source=self.source,
            content={
                'full_name': full_name,
                'gender': row['SEX_CODE_CD'],
                'race': row['RACE'],
                'age_at_march_11_2016': row['CURRAGE'] if row['CURRAGE'] else None,
                'appointed_date': self._clean_date(row['APPOINTED_DATE'])
            })

    def _insert_badge_number(self, row, officer):
        for ind in xrange(1, 11):
            if row['STAR%d' % ind]:
                self.change_keeper.create(
                    OfficerBadgeNumber, source=self.source,
                    content={'officer': officer, 'star': row['STAR%d' % ind]})

    def handle(self, *args, **options):
        file_path = options['file']
        with open(file_path, 'rU') as file:
            reader = csv.DictReader(file)
            batch = []
            last_identity = None
            for row in tqdm(reader, desc='Importing officer identity'):
                identity = (
                    row['LAST_NME'], row['FIRST_NME'], row['SEX_CODE_CD'],
                    row['RACE'], row['CURRAGE'], row['APPOINTED_DATE'])
                if identity == last_identity:
                    batch.append(row)
                else:
                    self._process_batch(batch)
                    batch = [row]
                    last_identity = identity
            self._process_batch(batch)
