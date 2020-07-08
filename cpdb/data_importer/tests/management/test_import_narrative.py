from io import StringIO, BytesIO
from csv import DictWriter
from mock import patch

from django.test import TestCase
from django.core.management import call_command

from robber import expect

from data.factories import AllegationFactory, AttachmentFileFactory
from data.constants import MEDIA_TYPE_DOCUMENT
from data.models import AttachmentNarrative


class ImportNarrativeTestCase(TestCase):
    def setUp(self):
        allegation_1 = AllegationFactory(crid='121', coaccused_count=1)
        allegation_2 = AllegationFactory(crid='122', coaccused_count=2)

        AttachmentFileFactory(
            id=1121,
            allegation=allegation_1,
            title='CR document 1121',
            tag='CR',
            url='https://cr-document.com/1121',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url1121',
        ),
        AttachmentFileFactory(
            id=1122,
            allegation=allegation_2,
            title='CR document 1122',
            tag='CR',
            url='https://cr-document.com/1122',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url1122',
        ),

        csv_content = StringIO()
        writer = DictWriter(
            csv_content,
            fieldnames=[
                'cr_id',
                'pdf_name',
                'page_num',
                'section_name',
                'column_name',
                'text',
                'batch_id',
                'dropbox_path',
                'doccloud_url'
            ]
        )
        writer.writeheader()
        writer.writerows([
            {
                'cr_id': '122',
                'pdf_name': 'LOG_5125812.pdf',
                'page_num': '2',
                'section_name': 'Incident Finding / Overall Case Finding',
                'column_name': 'Finding',
                'text': '(None Entered)',
                'batch_id': '2',
                'dropbox_path': '/Green v. CPD FOIA Files/Raw documents from Green v CPD/Green 2020_04_30',
                'doccloud_url': 'https://cr-document.com/1122',
            },
            {
                'cr_id': '122',
                'pdf_name': 'LOG_5125812.pdf',
                'page_num': '1',
                'section_name': 'Incident Finding / Overall Case Finding',
                'column_name': 'Finding',
                'text': 'NO AFFIDAVIT',
                'batch_id': '2',
                'dropbox_path': '/Green v. CPD FOIA Files/Raw documents from Green v CPD/Green 2020_04_30',
                'doccloud_url': 'https://cr-document.com/1122',
            },
            {
                'cr_id': '121',
                'pdf_name': 'LOG_123551.pdf',
                'page_num': '1',
                'section_name': 'Accused Members',
                'column_name': 'Initial / Intake Allegation',
                'text': 'It is alleged that the accused officer failed to secure his weapon',
                'batch_id': '1',
                'dropbox_path': '/Green v. CPD FOIA Files/Raw documents from Green v CPD/Green 2020_03_31',
                'doccloud_url': 'https://cr-document.com/1121',
            },
            {
                'cr_id': '121',
                'pdf_name': 'LOG_123551.pdf',
                'page_num': '2',
                'section_name': 'Current Allegations',
                'column_name': 'Allegation',
                'text': 'It is alleged by the complainant Sergeant Victoria STANEK #2012 Assigned to the 8th District',
                'batch_id': '1',
                'dropbox_path': '/Green v. CPD FOIA Files/Raw documents from Green v CPD/Green 2020_03_31',
                'doccloud_url': 'https://cr-document.com/1121',
            },
            {
                'cr_id': '123',
                'pdf_name': 'LOG_927344.pdf',
                'page_num': '1',
                'section_name': 'Current Allegations',
                'column_name': 'Allegation',
                'text': 'P.O. Christine TAYLOR alleges that on 29 DEC 11 between 0845 hours and 1120 hours',
                'batch_id': '2',
                'dropbox_path': '/Green v. CPD FOIA Files/Raw documents from Green v CPD/Green 2020_04_30',
                'doccloud_url': 'https://cr-document.com/1123',
            },
        ])
        self.csv_stream = BytesIO(csv_content.getvalue().encode('utf-8'))

    @patch('builtins.print')
    @patch('urllib.request.urlopen')
    def test_handle(self, urlopen_mock, print_mock):
        urlopen_mock.return_value = self.csv_stream
        call_command('import_narrative', narrative_url='https://cpdp.co/narrative.csv')

        expect(urlopen_mock).to.be.called_with('https://cpdp.co/narrative.csv')

        created_attachment_narratives = AttachmentNarrative.objects.all()
        expect(len(created_attachment_narratives)).to.eq(4)

        expect(created_attachment_narratives[0].attachment_id).to.eq(1121)
        expect(created_attachment_narratives[0].page_num).to.eq(1)
        expect(created_attachment_narratives[0].section_name).to.eq('Accused Members')
        expect(created_attachment_narratives[0].column_name).to.eq('Initial / Intake Allegation')
        expect(created_attachment_narratives[0].text_content).to.eq(
            'It is alleged that the accused officer failed to secure his weapon'
        )

        expect(created_attachment_narratives[1].attachment_id).to.eq(1121)
        expect(created_attachment_narratives[1].page_num).to.eq(2)
        expect(created_attachment_narratives[1].section_name).to.eq('Current Allegations')
        expect(created_attachment_narratives[1].column_name).to.eq('Allegation')
        expect(created_attachment_narratives[1].text_content).to.eq(
            'It is alleged by the complainant Sergeant Victoria STANEK #2012 Assigned to the 8th District'
        )

        expect(created_attachment_narratives[2].attachment_id).to.eq(1122)
        expect(created_attachment_narratives[2].page_num).to.eq(1)
        expect(created_attachment_narratives[2].section_name).to.eq('Incident Finding / Overall Case Finding')
        expect(created_attachment_narratives[2].column_name).to.eq('Finding')
        expect(created_attachment_narratives[2].text_content).to.eq('NO AFFIDAVIT')

        expect(created_attachment_narratives[3].attachment_id).to.eq(1122)
        expect(created_attachment_narratives[3].page_num).to.eq(2)
        expect(created_attachment_narratives[3].section_name).to.eq('Incident Finding / Overall Case Finding')
        expect(created_attachment_narratives[3].column_name).to.eq('Finding')
        expect(created_attachment_narratives[3].text_content).to.eq('(None Entered)')

        expect(print_mock).to.be.any_call('Found narratives: 4')
        expect(print_mock).to.be.any_call('Missing narratives: 1')
        expect(print_mock).to.be.any_call('=== START Missing Narratives ===')
        expect(print_mock).to.be.any_call([['123', 'LOG_927344.pdf', 'https://cr-document.com/1123']])
        expect(print_mock).to.be.any_call('=== END Missing Narratives ===')
