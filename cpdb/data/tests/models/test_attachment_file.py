import json
from urllib.error import HTTPError

from django.test import override_settings
from django.test.testcases import TestCase
from documentcloud import DoesNotExistError
from mock import patch, Mock
from robber import expect

from data.constants import AttachmentSourceType
from data.factories import AttachmentFileFactory, AllegationFactory
from data.models import AttachmentFile


class AttachmentFileTestCase(TestCase):
    def test_str(selfs):
        attachment = AttachmentFileFactory(title='Attachment title')
        expect(str(attachment)).to.eq('Attachment title')

    @override_settings(S3_BUCKET_PDF_DIRECTORY='pdf')
    def test_s3_key(self):
        attachment = AttachmentFileFactory(external_id='123')
        expect(attachment.s3_key).to.eq('pdf/123')

    @override_settings(
        S3_BUCKET_OFFICER_CONTENT='officer-content-test',
        S3_BUCKET_PDF_DIRECTORY='pdf',
        LAMBDA_FUNCTION_UPLOAD_PDF='uploadPdfTest'
    )
    @patch('data.models.attachment_file.aws')
    def test_upload_to_s3(self, mock_aws):
        attachment = AttachmentFileFactory(
            external_id='123',
            url='http://www.chicagocopa.org/wp-content/uploads/2016/05/CHI-R-00000105.pdf'
        )

        attachment.upload_to_s3()

        expect(mock_aws.lambda_client.invoke_async).to.be.any_call(
            FunctionName='uploadPdfTest',
            InvokeArgs=json.dumps({
                'url': 'http://www.chicagocopa.org/wp-content/uploads/2016/05/CHI-R-00000105.pdf',
                'bucket': 'officer-content-test',
                'key': 'pdf/123'
            })
        )

    def test_attachment_shown_manager(self):
        AttachmentFileFactory(id=1)
        AttachmentFileFactory(id=2, show=False)
        AttachmentFileFactory(id=3, show=False)

        shown_attachments = AttachmentFile.showing.all()

        expect(shown_attachments).to.have.length(1)
        expect(shown_attachments[0].id).to.eq(1)

    def test_linked_documents(self):
        allegation = AllegationFactory()
        attachment = AttachmentFileFactory(owner=allegation, show=True)
        linked_document1 = AttachmentFileFactory(owner=allegation, file_type='document', show=True)
        linked_document2 = AttachmentFileFactory(owner=allegation, file_type='document', show=True)
        not_showing_linked_document = AttachmentFileFactory(owner=allegation, file_type='document', show=False)
        audio = AttachmentFileFactory(owner=allegation, file_type='audio', show=True)
        video = AttachmentFileFactory(owner=allegation, file_type='video', show=True)

        expect(attachment.linked_documents).to.contain(linked_document1)
        expect(attachment.linked_documents).to.contain(linked_document2)
        expect(attachment.linked_documents).not_to.contain(not_showing_linked_document)
        expect(attachment.linked_documents).not_to.contain(audio)
        expect(attachment.linked_documents).not_to.contain(video)

    def test_default_reprocess_text_count(self):
        attachment = AttachmentFileFactory(show=True)
        expect(attachment.reprocess_text_count).to.equal(0)

    def test_update_allegation_summary(self):
        text_content = \
            'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY ' \
            '\nSUMMARY REPORT OF INVESTIGATION1' \
            '\nI. EXECUTIVE SUMMARY' \
            '\nDate of Incident: September 25, 2015' \
            '\nTime of Incident: 8:53 pm.' \
            '\nLocation of Incident: N. Central Park Avenue, Chicago, IL' \
            '\nDate of COPA Notification: September 25, 2015' \
            '\nTime of COPA Notification: 9:15 pm.' \
            '\nOn September 25, 2015, at approximately 8:50 pm, Officers A and responded to a' \
            '\ncall of a disturbance with a mentally ill subject, Involved Civilian 1 (Involved Civilian 1), at ' \
            '\nN. Central Park Avenue, Chicago, IL. Upon arrival, the officers met with Involved Civilian' \
            '\nmother, Involved Civilian 2 (Involved Civilian 2), who stated that Involved Civilian 1 was acting' \
            '\ncrazy, had a knife, and would not come out of his bedroom. Officers A and B, along with assisting' \
            '\nOfficers and D, entered the residence and knocked on Involved Civilian bedroom door.' \
            '\nInvolved Civilian 1 opened the bedroom door while holding a knife in his hand. The officers' \
            '\nordered Involved Civilian 1 to drop the knife, but he did not comply. Involved Civilian 1 exited' \
            '\nhis bedroom and approached Officer A as he stood in the kitchen, which was adjacent to the' \
            '\nbedroom. Officer attempted to tase Involved Civilian 1, but the Taser did not appear to have any' \
            '\neffect on Involved Civilian 1. Involved Civilian 1 continued to approach Officer A, while still' \
            '\nholding the knife in his hand, at which time Officer A discharged his firearm five times, striking' \
            '\nInvolved Civilian 1 several times about the body. Involved Civilian 1 was declared dead at 2133' \
            '\nhours at Mt. Sinai hospital. investigation demonstrates that Officer use of deadly' \
            '\nforce complied with Chicago Police Department rules and directives.' \
            '\nII. INVOLVED PARTIES' \
            '\nInvolved Officer Officer A, star Employee Date of' \
            '\nAppointment: Chicago Police Officer, Unit of' \
            '\nAssignment: XX, DOB: 1983, Male White.' \
            '\nInvolved Individual#1: Involved Civilian 1, DOB: 1982, Male, Black.' \
            '\n1 On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the ' \
            '\nIndependent Police' \

        allegation = AllegationFactory(summary='')
        attachment_file = AttachmentFileFactory(
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
            text_content=text_content,
            owner=allegation,
        )

        expect(attachment_file.update_allegation_summary()).to.be.true()

        expect(allegation.summary).to.eq(
            'On September 25, 2015, at approximately 8:50 pm, Officers A and responded to a '
            'call of a disturbance with a mentally ill subject, Involved Civilian 1 (Involved Civilian 1), at '
            'N. Central Park Avenue, Chicago, IL. Upon arrival, the officers met with Involved Civilian '
            'mother, Involved Civilian 2 (Involved Civilian 2), who stated that Involved Civilian 1 was acting '
            'crazy, had a knife, and would not come out of his bedroom. Officers A and B, along with assisting '
            'Officers and D, entered the residence and knocked on Involved Civilian bedroom door. '
            'Involved Civilian 1 opened the bedroom door while holding a knife in his hand. The officers '
            'ordered Involved Civilian 1 to drop the knife, but he did not comply. Involved Civilian 1 exited '
            'his bedroom and approached Officer A as he stood in the kitchen, which was adjacent to the '
            'bedroom. Officer attempted to tase Involved Civilian 1, but the Taser did not appear to have any '
            'effect on Involved Civilian 1. Involved Civilian 1 continued to approach Officer A, while still '
            'holding the knife in his hand, at which time Officer A discharged his firearm five times, striking '
            'Involved Civilian 1 several times about the body. Involved Civilian 1 was declared dead at 2133 '
            'hours at Mt. Sinai hospital. investigation demonstrates that Officer use of deadly '
            'force complied with Chicago Police Department rules and directives.'
            )

        expect(allegation.is_extracted_summary).to.be.true()

    def test_update_allegation_summary_not_update_if_source_type_does_not_match(self):
        text_content = \
            'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY ' \
            '\nSUMMARY REPORT OF INVESTIGATION1' \
            '\nI. EXECUTIVE SUMMARY' \
            '\nDate of Incident: September 25, 2015' \
            '\nTime of Incident: 8:53 pm.' \
            '\nLocation of Incident: N. Central Park Avenue, Chicago, IL' \
            '\nDate of COPA Notification: September 25, 2015' \
            '\nTime of COPA Notification: 9:15 pm.' \
            '\nOn September 25, 2015, at approximately 8:50 pm, Officers A and responded to a' \
            '\ncall of a disturbance with a mentally ill subject, Involved Civilian 1 (Involved Civilian 1), at ' \
            '\nN. Central Park Avenue, Chicago, IL. Upon arrival, the officers met with Involved Civilian' \
            '\nmother, Involved Civilian 2 (Involved Civilian 2), who stated that Involved Civilian 1 was acting' \
            '\ncrazy, had a knife, and would not come out of his bedroom. Officers A and B, along with assisting' \
            '\nOfficers and D, entered the residence and knocked on Involved Civilian bedroom door.' \
            '\nInvolved Civilian 1 opened the bedroom door while holding a knife in his hand. The officers' \
            '\nordered Involved Civilian 1 to drop the knife, but he did not comply. Involved Civilian 1 exited' \
            '\nhis bedroom and approached Officer A as he stood in the kitchen, which was adjacent to the' \
            '\nbedroom. Officer attempted to tase Involved Civilian 1, but the Taser did not appear to have any' \
            '\neffect on Involved Civilian 1. Involved Civilian 1 continued to approach Officer A, while still' \
            '\nholding the knife in his hand, at which time Officer A discharged his firearm five times, striking' \
            '\nInvolved Civilian 1 several times about the body. Involved Civilian 1 was declared dead at 2133' \
            '\nhours at Mt. Sinai hospital. investigation demonstrates that Officer use of deadly' \
            '\nforce complied with Chicago Police Department rules and directives.' \
            '\nII. INVOLVED PARTIES' \
            '\nInvolved Officer Officer A, star Employee Date of' \
            '\nAppointment: Chicago Police Officer, Unit of' \
            '\nAssignment: XX, DOB: 1983, Male White.' \
            '\nInvolved Individual#1: Involved Civilian 1, DOB: 1982, Male, Black.' \
            '\n1 On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the ' \
            '\nIndependent Police' \

        allegation = AllegationFactory(summary='')
        attachment_file = AttachmentFileFactory(
            source_type=AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            text_content=text_content,
            owner=allegation,
        )

        expect(attachment_file.update_allegation_summary()).to.be.false()

        expect(allegation.summary).to.eq('')
        expect(allegation.is_extracted_summary).to.be.false()

    def test_update_allegation_summary_not_update_if_do_not_have_text_content(self):
        allegation = AllegationFactory(summary='')
        attachment_file = AttachmentFileFactory(
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
            text_content='',
            owner=allegation,
        )

        expect(attachment_file.update_allegation_summary()).to.be.false()

        expect(allegation.summary).to.eq('')
        expect(allegation.is_extracted_summary).to.be.false()

    def test_update_allegation_summary_not_update_if_allegation_already_has_summary(self):
        text_content = \
            'CIVILIAN OFFICE OF POLICE ACCOUNTABILITY ' \
            '\nSUMMARY REPORT OF INVESTIGATION1' \
            '\nI. EXECUTIVE SUMMARY' \
            '\nDate of Incident: September 25, 2015' \
            '\nTime of Incident: 8:53 pm.' \
            '\nLocation of Incident: N. Central Park Avenue, Chicago, IL' \
            '\nDate of COPA Notification: September 25, 2015' \
            '\nTime of COPA Notification: 9:15 pm.' \
            '\nOn September 25, 2015, at approximately 8:50 pm, Officers A and responded to a' \
            '\ncall of a disturbance with a mentally ill subject, Involved Civilian 1 (Involved Civilian 1), at ' \
            '\nN. Central Park Avenue, Chicago, IL. Upon arrival, the officers met with Involved Civilian' \
            '\nmother, Involved Civilian 2 (Involved Civilian 2), who stated that Involved Civilian 1 was acting' \
            '\ncrazy, had a knife, and would not come out of his bedroom. Officers A and B, along with assisting' \
            '\nOfficers and D, entered the residence and knocked on Involved Civilian bedroom door.' \
            '\nInvolved Civilian 1 opened the bedroom door while holding a knife in his hand. The officers' \
            '\nordered Involved Civilian 1 to drop the knife, but he did not comply. Involved Civilian 1 exited' \
            '\nhis bedroom and approached Officer A as he stood in the kitchen, which was adjacent to the' \
            '\nbedroom. Officer attempted to tase Involved Civilian 1, but the Taser did not appear to have any' \
            '\neffect on Involved Civilian 1. Involved Civilian 1 continued to approach Officer A, while still' \
            '\nholding the knife in his hand, at which time Officer A discharged his firearm five times, striking' \
            '\nInvolved Civilian 1 several times about the body. Involved Civilian 1 was declared dead at 2133' \
            '\nhours at Mt. Sinai hospital. investigation demonstrates that Officer use of deadly' \
            '\nforce complied with Chicago Police Department rules and directives.' \
            '\nII. INVOLVED PARTIES' \
            '\nInvolved Officer Officer A, star Employee Date of' \
            '\nAppointment: Chicago Police Officer, Unit of' \
            '\nAssignment: XX, DOB: 1983, Male White.' \
            '\nInvolved Individual#1: Involved Civilian 1, DOB: 1982, Male, Black.' \
            '\n1 On September 15, 2017, the Civilian Office of Police Accountability (COPA) replaced the ' \
            '\nIndependent Police' \

        allegation = AllegationFactory(summary='This allegation already has summary.')
        attachment_file = AttachmentFileFactory(
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
            text_content=text_content,
            owner=allegation,
        )

        expect(attachment_file.update_allegation_summary()).to.be.false()

        expect(allegation.summary).to.eq('This allegation already has summary.')
        expect(allegation.is_extracted_summary).to.be.false()

    def test_update_allegation_summary_not_update_if_can_not_parse_summary_from_text_content(self):
        text_content = 'This is invalid text content.'
        allegation = AllegationFactory(summary='')
        attachment_file = AttachmentFileFactory(
            source_type=AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD,
            text_content=text_content,
            owner=allegation,
        )

        expect(attachment_file.update_allegation_summary()).to.be.false()

        expect(allegation.summary).to.eq('')
        expect(allegation.is_extracted_summary).to.be.false()


class UpdateToDocumentcloudTestCase(TestCase):
    def setUp(self):
        self.document_cloud_patcher = patch('data.models.attachment_file.DocumentCloud')
        self.logger_patcher = patch('data.models.attachment_file.logger')

        self.mock_DocumentCloud = self.document_cloud_patcher.start()
        self.mock_logger = self.logger_patcher.start()

        self.mock_client = Mock()
        self.mock_doc = Mock()
        self.mock_client.documents.get.return_value = self.mock_doc

        self.mock_DocumentCloud.return_value = self.mock_client

    def tearDown(self):
        self.document_cloud_patcher.stop()
        self.logger_patcher.stop()

    def test_not_update_with_wrong_source_type(self):
        attachment = AttachmentFileFactory(source_type='something wrong')
        attachment.update_to_documentcloud('title', 'some title')
        expect(self.mock_client.documents.get).not_to.be.called()
        expect(self.mock_doc.save).not_to.be.called()
        expect(self.mock_logger.error).not_to.be.called()

    def test_not_update_when_cannot_get_documentcloud_document(self):
        self.mock_client.documents.get.side_effect = DoesNotExistError()
        attachment = AttachmentFileFactory(external_id=1, source_type='DOCUMENTCLOUD')
        attachment.update_to_documentcloud('title', 'some title')

        expect(self.mock_doc.save).not_to.be.called()
        expect(self.mock_logger.error).to.be.called_with('Cannot find document with external id 1 on DocumentCloud')

    def test_not_update_when_cannot_save_documentcloud_document(self):
        self.mock_doc.save.side_effect = HTTPError('', '404', '', None, None)
        attachment = AttachmentFileFactory(external_id=1, source_type='DOCUMENTCLOUD')
        attachment.update_to_documentcloud('title', 'some title')

        expect(self.mock_doc.title).to.be.eq('some title')
        expect(self.mock_logger.error).to.be.called_with('Cannot save document with external id 1 on DocumentCloud')

    def test_not_update_when_no_change(self):
        attachment = AttachmentFileFactory(external_id=1, source_type='DOCUMENTCLOUD', title='no changed title')
        setattr(self.mock_doc, 'title', 'no changed title')

        attachment.update_to_documentcloud('title', 'no changed title')

        expect(self.mock_client.documents.get).to.be.called_with(1)
        expect(self.mock_doc.save).not_to.be.called()

    def test_update_successfully(self):
        attachment = AttachmentFileFactory(external_id=1, source_type='DOCUMENTCLOUD')
        attachment.update_to_documentcloud('title', 'some title')

        expect(self.mock_client.documents.get).to.be.called_with(1)
        expect(self.mock_doc.save).to.be.called()
        expect(self.mock_logger.error).not_to.be.called()
        expect(self.mock_doc.title).to.be.eq('some title')
