from datetime import datetime
from operator import itemgetter

from django.test import TestCase
from freezegun import freeze_time

from robber import expect
import pytz

from data.factories import AttachmentFileFactory, UserFactory, AllegationFactory
from tracker.serializers import AttachmentFileSerializer, AuthenticatedAttachmentFileSerializer


class AttachmentFileSerializerSerializerTestCase(TestCase):
    def test_serialization(self):
        user = UserFactory(username='test user')
        allegation = AllegationFactory(crid='456')
        attachment = AttachmentFileFactory(
            id=123,
            owner=allegation,
            title='CR document',
            text_content='CHICAGO POLICE DEPARTMENT RD I HT334604',
            url='http://foo.com',
            preview_image_url='https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            source_type='DOCUMENTCLOUD',
            show=True,
            file_type='document',
            pages=10,
            last_updated_by=user,
            views_count=100
        )
        attachment.created_at = datetime(2017, 8, 4, 14, 30, 00, tzinfo=pytz.utc)
        with freeze_time('2017-08-05 12:00:01'):
            attachment.save()

        AttachmentFileFactory(
            id=124,
            owner=allegation,
            show=True,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/124/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
        )
        AttachmentFileFactory(
            id=125,
            owner=allegation,
            show=True,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
        )
        AttachmentFileFactory(
            id=126,
            owner=allegation,
            show=False,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
        )
        AttachmentFileFactory(
            id=127,
            owner=allegation,
            show=True,
            file_type='audio',
            preview_image_url='',
            original_url='http://audio_link',
        )

        expected_data = {
            'id': 123,
            'crid': '456',
            'title': 'CR document',
            'text_content': 'CHICAGO POLICE DEPARTMENT RD I HT334604',
            'url': 'http://foo.com',
            'preview_image_url': 'https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
            'original_url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'created_at': '2017-08-04T09:30:00-05:00',
            'updated_at': '2017-08-05T07:00:01-05:00',
            'crawler_name': 'Document Cloud',
            'linked_documents': [
                {
                    'id': 124,
                    'preview_image_url': 'https://assets.documentcloud.org/124/CRID-456-CR-p1-normal.gif',
                },
                {
                    'id': 125,
                    'preview_image_url': 'https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
                }
            ],
            'pages': 10,
            'last_updated_by': 'test user'
        }

        data = AttachmentFileSerializer(attachment).data

        data['linked_documents'] = sorted(data['linked_documents'], key=itemgetter('id'))

        expect(data).to.eq(expected_data)


class AuthenticatedAttachmentFileSerializerTestCase(TestCase):
    def test_serialization(self):
        user = UserFactory(username='test user')

        allegation = AllegationFactory(crid='456')

        with freeze_time('2017-08-04 14:30:00'):
            attachment = AttachmentFileFactory(
                id=123,
                owner=allegation,
                title='CR document',
                text_content='CHICAGO POLICE DEPARTMENT RD I HT334604',
                url='http://foo.com',
                preview_image_url='https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
                original_url='https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
                source_type='DOCUMENTCLOUD',
                show=True,
                file_type='document',
                pages=10,
                last_updated_by=user,
                views_count=100,
                downloads_count=99,
                notifications_count=200,
                tags=['tag123']
            )

        with freeze_time('2017-08-05 12:00:01'):
            attachment.save()

        AttachmentFileFactory(
            id=124,
            owner=allegation,
            show=True,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/124/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
            tags=['tag124'],
        )
        AttachmentFileFactory(
            id=125,
            owner=allegation,
            show=True,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
            tags=['tag125'],
        )
        AttachmentFileFactory(
            id=126,
            owner=allegation,
            show=False,
            file_type='document',
            preview_image_url='https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
            original_url='https://www.documentcloud.org/documents/1-CRID-123-CR.html',
        )
        AttachmentFileFactory(
            id=127,
            owner=allegation,
            show=True,
            file_type='audio',
            preview_image_url='',
            original_url='http://audio_link',
            tags=['tag127'],
        )

        expected_data = {
            'id': 123,
            'crid': '456',
            'title': 'CR document',
            'text_content': 'CHICAGO POLICE DEPARTMENT RD I HT334604',
            'url': 'http://foo.com',
            'preview_image_url': 'https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif',
            'original_url': 'https://www.documentcloud.org/documents/1-CRID-123456-CR.html',
            'created_at': '2017-08-04T09:30:00-05:00',
            'updated_at': '2017-08-05T07:00:01-05:00',
            'crawler_name': 'Document Cloud',
            'linked_documents': [
                {
                    'id': 124,
                    'preview_image_url': 'https://assets.documentcloud.org/124/CRID-456-CR-p1-normal.gif',
                },
                {
                    'id': 125,
                    'preview_image_url': 'https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif',
                }
            ],
            'pages': 10,
            'last_updated_by': 'test user',
            'views_count': 100,
            'downloads_count': 99,
            'notifications_count': 200,
            'tags': ['tag123'],
            'next_document_id': 126,
        }

        data = AuthenticatedAttachmentFileSerializer(attachment).data
        data['linked_documents'] = sorted(data['linked_documents'], key=itemgetter('id'))

        expect(data).to.eq(expected_data)

    def test_next_document_id_return_next_untagged_document_id(self):
        allegation = AllegationFactory(crid='456')
        with freeze_time('2017-08-04'):
            next_attachment = AttachmentFileFactory(
                owner=allegation,
                file_type='document',
            )

        with freeze_time('2017-08-07'):
            AttachmentFileFactory(
                owner=allegation,
                file_type='audio',
            )

        with freeze_time('2017-08-10'):
            AttachmentFileFactory(
                owner=allegation,
                file_type='document',
                tags=['tag1'],
            )

        with freeze_time('2017-09-04'):
            attachment = AttachmentFileFactory(
                owner=allegation,
                file_type='document',
            )

        with freeze_time('2017-10-04'):
            AttachmentFileFactory(
                owner=allegation,
                file_type='document',
            )

        next_document_id = AuthenticatedAttachmentFileSerializer(attachment).data['next_document_id']
        expect(next_document_id).to.eq(next_attachment.id)

    def test_next_document_id_most_recent_untagged_document_id_if_current_document_is_oldest(self):
        allegation = AllegationFactory(crid='456')

        with freeze_time('2017-08-04'):
            attachment = AttachmentFileFactory(
                owner=allegation,
                file_type='document',
            )

        with freeze_time('2017-09-04'):
            AttachmentFileFactory(
                owner=allegation,
                file_type='document',
            )

        with freeze_time('2017-10-04'):
            next_attachment = AttachmentFileFactory(
                owner=allegation,
                file_type='document',
            )

        with freeze_time('2017-10-05'):
            AttachmentFileFactory(
                owner=allegation,
                file_type='audio',
            )

        with freeze_time('2017-10-06'):
            AttachmentFileFactory(
                owner=allegation,
                file_type='document',
                tags=['tag1']
            )

        next_document_id = AuthenticatedAttachmentFileSerializer(attachment).data['next_document_id']
        expect(next_document_id).to.eq(next_attachment.id)

    def test_next_document_id_is_none_if_all_documents_have_tags(self):
        allegation = AllegationFactory(crid='456')
        with freeze_time('2017-08-04'):
            AttachmentFileFactory(
                owner=allegation,
                file_type='document',
                tags=['tag123'],
            )

        with freeze_time('2017-09-04'):
            AttachmentFileFactory(
                owner=allegation,
                file_type='document',
                tags=['tag124'],
            )

        with freeze_time('2017-10-05'):
            attachment = AttachmentFileFactory(
                owner=allegation,
                file_type='document',
                tags=['tag125'],
            )

        with freeze_time('2017-08-05'):
            AttachmentFileFactory(
                owner=allegation,
                file_type='audio',
            )

        next_document_id = AuthenticatedAttachmentFileSerializer(attachment).data['next_document_id']
        expect(next_document_id).to.eq(None)
