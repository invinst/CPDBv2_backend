import inspect
import filecmp
import shutil
import os
from subprocess import call

from django.test import TestCase
from robber import expect


class WriterBaseTestCase(TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(inspect.getfile(self.__class__))
        self.test_output_dir = f'{self.test_dir}/output'

        shutil.rmtree(self.test_output_dir, ignore_errors=True)

    def tearDown(self):
        shutil.rmtree(self.test_output_dir, ignore_errors=True)

    def covert_xlsx_to_csv(self, filename):
        call([
            'xlsx2csv',
            f'{self.test_output_dir}/{filename}',
            self.test_output_dir,
            '-a'
        ])

    def assert_csv_files_equal(self, expectation_dir, sheet_names):
        for sheet_name in sheet_names:
            expect(
                filecmp.cmp(
                    f'{self.test_output_dir}/{sheet_name}.csv',
                    f'{self.test_dir}/csv/{expectation_dir}/{sheet_name}.csv'
                )
            ).to.be.true()
