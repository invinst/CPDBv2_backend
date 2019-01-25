import filecmp
import os
import inspect
import shutil
from io import BytesIO
from unittest import TestCase
from zipfile import ZipFile

import boto3
from moto import mock_s3
from robber import expect

from create_officer_zip.lambda_function import lambda_handler


class LambdaFunctionTestCase(TestCase):
    def init_s3(self):
        # Because of mock_s3 we need to invoke this inside test function instead of defining setup
        self.test_dir = os.path.dirname(inspect.getfile(self.__class__))
        self.officer_id = 1
        self.bucket = 'officer-content-test'
        self.s3 = boto3.resource('s3', region_name='us-east-1')

        self.s3.create_bucket(Bucket=self.bucket)
        self.s3.Object(self.bucket, f'xlsx/{self.officer_id}/accused.xlsx').upload_file(
            f'{self.test_dir}/xlsx/accused.xlsx'
        )
        self.s3.Object(self.bucket, f'xlsx/{self.officer_id}/investigator.xlsx').upload_file(
            f'{self.test_dir}/xlsx/investigator.xlsx'
        )
        self.s3.Object(self.bucket, f'xlsx/{self.officer_id}/use_of_force.xlsx').upload_file(
            f'{self.test_dir}/xlsx/use_of_force.xlsx'
        )

    def tearDown(self):
        shutil.rmtree(f'{self.test_dir}/tmp', ignore_errors=True)

    @mock_s3
    def test_lambda_handler_without_attachments(self):
        self.init_s3()
        key = 'zip/officer_1_without_docs.zip'
        lambda_handler(
            event={
                'officer_id': self.officer_id,
                'key': key,
                'bucket': self.bucket,
                'xlsx_dir': 'xlsx',
                'pdf_dir': 'pdf',
                'allegation_attachments_dict': {},
                'investigator_attachments_dict': {},
            },
            context=None
        )

        s3_file_buffer = BytesIO(self.s3.Object(self.bucket, key).get()['Body'].read())
        zip_ref = ZipFile(s3_file_buffer, 'r')
        zip_ref.extractall(f'{self.test_dir}/tmp')
        zip_ref.close()

        expect(set(os.listdir(f'{self.test_dir}/tmp'))).to.eq({
            'investigator.xlsx', 'use_of_force.xlsx', 'accused.xlsx'
        })

        expect(filecmp.cmp(
            f'{self.test_dir}/tmp/accused.xlsx',
            f'{self.test_dir}/xlsx/accused.xlsx')
        ).to.be.true()
        expect(filecmp.cmp(
            f'{self.test_dir}/tmp/investigator.xlsx',
            f'{self.test_dir}/xlsx/investigator.xlsx')
        ).to.be.true()
        expect(filecmp.cmp(
            f'{self.test_dir}/tmp/use_of_force.xlsx',
            f'{self.test_dir}/xlsx/use_of_force.xlsx')
        ).to.be.true()

    @mock_s3
    def test_lambda_handler_with_attachments(self):
        self.init_s3()
        self.s3.Object(self.bucket, 'pdf/2646152').upload_file(f'{self.test_dir}/pdf/2646152')
        self.s3.Object(self.bucket, 'pdf/2646153').upload_file(f'{self.test_dir}/pdf/2646153')

        key = 'zip/officer_1.zip'
        lambda_handler(
            event={
                'officer_id': self.officer_id,
                'key': key,
                'bucket': self.bucket,
                'xlsx_dir': 'xlsx',
                'pdf_dir': 'pdf',
                'allegation_attachments_dict': {
                    '2646152': 'attachment_1.pdf',
                    'not_exist_external_id': 'should_not_added.pdf'
                },
                'investigator_attachments_dict': {'2646153': 'attachment_2.pdf'},
            },
            context=None
        )

        s3_file_buffer = BytesIO(self.s3.Object(self.bucket, key).get()['Body'].read())
        zip_ref = ZipFile(s3_file_buffer, 'r')
        zip_ref.extractall(f'{self.test_dir}/tmp')
        zip_ref.close()

        expect(set(os.listdir(f'{self.test_dir}/tmp'))).to.eq({
            'investigator.xlsx', 'use_of_force.xlsx', 'investigators', 'accused.xlsx', 'documents'
        })
        expect(os.listdir(f'{self.test_dir}/tmp/documents')).to.eq(['attachment_1.pdf'])
        expect(os.listdir(f'{self.test_dir}/tmp/investigators')).to.eq(['attachment_2.pdf'])

        expect(filecmp.cmp(
            f'{self.test_dir}/tmp/accused.xlsx',
            f'{self.test_dir}/xlsx/accused.xlsx')
        ).to.be.true()
        expect(filecmp.cmp(
            f'{self.test_dir}/tmp/investigator.xlsx',
            f'{self.test_dir}/xlsx/investigator.xlsx')
        ).to.be.true()
        expect(filecmp.cmp(
            f'{self.test_dir}/tmp/use_of_force.xlsx',
            f'{self.test_dir}/xlsx/use_of_force.xlsx')
        ).to.be.true()

        expect(filecmp.cmp(
            f'{self.test_dir}/tmp/documents/attachment_1.pdf',
            f'{self.test_dir}/pdf/2646152')
        ).to.be.true()
        expect(filecmp.cmp(
            f'{self.test_dir}/tmp/investigators/attachment_2.pdf',
            f'{self.test_dir}/pdf/2646153')
        ).to.be.true()
