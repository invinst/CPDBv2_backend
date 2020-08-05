from io import StringIO, BytesIO
from csv import DictWriter
from mock import patch

from django.test import TestCase
from django.core.management import call_command

from robber import expect

from data.factories import AllegationFactory, AttachmentFileFactory
from data.constants import MEDIA_TYPE_DOCUMENT
from data.models import AttachmentOCR, AttachmentFile


class ImportOCRTestCase(TestCase):
    def setUp(self):
        allegation_1 = AllegationFactory(crid='121', coaccused_count=1)
        allegation_2 = AllegationFactory(crid='122', coaccused_count=2)

        AttachmentFileFactory(
            id=1121,
            owner=allegation_1,
            title='CR document 1121',
            tag='CR',
            url='https://cr-document.com/1121',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url1121',
        ),
        AttachmentFileFactory(
            id=1122,
            owner=allegation_2,
            title='CR document 1122',
            tag='CR',
            url='https://cr-document.com/1122',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url1122',
        ),

        csv_content = StringIO()
        writer = DictWriter(
            csv_content,
            fieldnames=['cr_id', 'filename', 'page_num', 'batch_name', 'doccloud_url', 'ocr_text']
        )
        writer.writeheader()
        writer.writerows([
            {
                'cr_id': '122',
                'filename': 'LOG_5125812.pdf',
                'page_num': '2',
                'batch_name': 'Green 2020_07_02',
                'doccloud_url': 'https://cr-document.com/1122',
                'ocr_text': 'text 1122_2'
            },
            {
                'cr_id': '122',
                'filename': 'LOG_5125812.pdf',
                'page_num': '1',
                'batch_name': 'Green 2020_07_02',
                'doccloud_url': 'https://cr-document.com/1122',
                'ocr_text': 'text 1122_1'
            },
            {
                'cr_id': '121',
                'filename': 'LOG_123551.pdf',
                'page_num': '1',
                'batch_name': 'Green 2020_04_30',
                'doccloud_url': 'https://cr-document.com/1121',
                'ocr_text': 'text 1121_1'
            },
            {
                'cr_id': '121',
                'filename': 'LOG_123551.pdf',
                'page_num': '2',
                'batch_name': 'Green 2020_04_30',
                'doccloud_url': 'https://cr-document.com/1121',
                'ocr_text': 'text 1121_2'
            },
            {
                'cr_id': '123',
                'filename': 'LOG_927344.pdf',
                'page_num': '1',
                'batch_name': 'Green 2020_12_20',
                'doccloud_url': 'https://cr-document.com/1123',
                'ocr_text': 'some missing document'
            },
        ])
        self.csv_stream = BytesIO(csv_content.getvalue().encode('utf-8'))

    @patch('builtins.print')
    @patch('urllib.request.urlopen')
    def test_handle(self, urlopen_mock, print_mock):
        urlopen_mock.return_value = self.csv_stream
        call_command('import_ocr', ocr_url='https://cpdp.co/ocr.csv')

        expect(urlopen_mock).to.be.called_with('https://cpdp.co/ocr.csv')

        created_attachment_ocrs = AttachmentOCR.objects.all()
        expect(len(created_attachment_ocrs)).to.eq(4)
        expect(created_attachment_ocrs[0].attachment_id).to.eq(1121)
        expect(created_attachment_ocrs[0].page_num).to.eq(1)
        expect(created_attachment_ocrs[0].ocr_text).to.eq('text 1121_1')

        expect(created_attachment_ocrs[1].attachment_id).to.eq(1121)
        expect(created_attachment_ocrs[1].page_num).to.eq(2)
        expect(created_attachment_ocrs[1].ocr_text).to.eq('text 1121_2')

        expect(created_attachment_ocrs[2].attachment_id).to.eq(1122)
        expect(created_attachment_ocrs[2].page_num).to.eq(1)
        expect(created_attachment_ocrs[2].ocr_text).to.eq('text 1122_1')

        expect(created_attachment_ocrs[3].attachment_id).to.eq(1122)
        expect(created_attachment_ocrs[3].page_num).to.eq(2)
        expect(created_attachment_ocrs[3].ocr_text).to.eq('text 1122_2')

        attachment_1121 = AttachmentFile.objects.get(id=1121)
        expect(attachment_1121.is_external_ocr).to.be.true()
        expect(attachment_1121.text_content).to.eq('text 1121_1\ntext 1121_2')

        attachment_1122 = AttachmentFile.objects.get(id=1122)
        expect(attachment_1122.is_external_ocr).to.be.true()
        expect(attachment_1122.text_content).to.eq('text 1122_1\ntext 1122_2')

        expect(print_mock).to.be.any_call('Updated attachment OCRs: 2')
        expect(print_mock).to.be.any_call('Found OCR pages: 4')
        expect(print_mock).to.be.any_call('Missing OCR pages: 1')
        expect(print_mock).to.be.any_call('=== START Missing OCR pages ===')
        expect(print_mock).to.be.any_call([['123', 'LOG_927344.pdf', 'https://cr-document.com/1123']])
        expect(print_mock).to.be.any_call('=== END Missing OCR pages ===')
