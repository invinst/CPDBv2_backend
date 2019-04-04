from datetime import datetime

import pytz
from django.test.testcases import TestCase

from robber.expect import expect
from freezegun import freeze_time

from analytics import constants
from analytics.factories import AttachmentTrackingFactory
from data.cache_managers import allegation_cache_manager
from data.constants import MEDIA_TYPE_DOCUMENT, MEDIA_TYPE_AUDIO, MEDIA_TYPE_VIDEO
from data.factories import AllegationFactory, AttachmentFileFactory, OfficerAllegationFactory, AllegationCategoryFactory
from cr.queries import LatestDocumentsQuery


class LatestDocumentsQueryTestCase(TestCase):
    @freeze_time('2019-04-03')
    def test_execute(self):
        allegation_1 = AllegationFactory(crid='123')
        allegation_2 = AllegationFactory(crid='456')
        allegation_3 = AllegationFactory(crid='789')
        allegation_4 = AllegationFactory(crid='321')
        allegation_5 = AllegationFactory(crid='987')

        allegation_category_1 = AllegationCategoryFactory(id=1)
        allegation_category_12 = AllegationCategoryFactory(id=2)

        OfficerAllegationFactory(allegation=allegation_1, allegation_category=allegation_category_1)
        OfficerAllegationFactory(allegation=allegation_1, allegation_category=allegation_category_1)
        OfficerAllegationFactory(allegation=allegation_1, allegation_category=allegation_category_12)

        attachment_file_1 = AttachmentFileFactory(
            allegation=allegation_1,
            title='CR document 1',
            id=1,
            tag='CR',
            url='http://cr-document.com/1',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url1',
            external_created_at=datetime(2019, 1, 19, 12, 1, 1, tzinfo=pytz.utc)
        )
        AttachmentFileFactory(
            allegation=allegation_1,
            title='CR document 2',
            id=2,
            tag='CR',
            url='http://cr-document.com/2',
            file_type=MEDIA_TYPE_DOCUMENT,
            external_created_at=datetime(2019, 1, 14, 10, 12, 1, tzinfo=pytz.utc)
        )

        attachment_file_2 = AttachmentFileFactory(
            allegation=allegation_2,
            title='CR document 3',
            id=3,
            tag='CR',
            url='http://cr-document.com/3',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url3',
            external_created_at=datetime(2019, 1, 15, 9, 3, 1, tzinfo=pytz.utc)
        )

        AttachmentFileFactory(
            allegation=allegation_2,
            title='CR document 4',
            id=4,
            tag='OCIR',
            url='http://cr-document.com/4',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url4',
            external_created_at=datetime(2019, 1, 19, 17, 12, 5, tzinfo=pytz.utc)
        )

        with freeze_time(datetime(2019, 1, 20, 13, 2, 15, tzinfo=pytz.utc)):
            AttachmentFileFactory(
                allegation=allegation_2,
                title='CR document 5',
                id=5,
                tag='AR',
                url='http://cr-document.com/5',
                file_type=MEDIA_TYPE_DOCUMENT,
                preview_image_url='http://preview.com/url5',
                external_created_at=None
            )

        AttachmentFileFactory(
            allegation=allegation_3,
            title='CR document 6',
            id=6,
            tag='CR',
            url='http://cr-document.com/6',
            file_type=MEDIA_TYPE_AUDIO,
            preview_image_url='http://preview.com/url6',
            external_created_at=datetime(2019, 1, 21, 6, 4, 12, tzinfo=pytz.utc)
        )

        AttachmentFileFactory(
            allegation=allegation_3,
            title='CR document 7',
            id=7,
            tag='CR',
            url='http://cr-document.com/7',
            file_type=MEDIA_TYPE_VIDEO,
            preview_image_url='http://preview.com/url7',
            external_created_at=datetime(2019, 1, 22, 4, 9, 12, tzinfo=pytz.utc)
        )

        attachment_file_3 = AttachmentFileFactory(
            title='Tracking document 1',
            id=8,
            tag='CR',
            url='http://cr-document.com/8',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url8',
            allegation=allegation_4,
            external_created_at=datetime(2014, 9, 14, 12, 0, 1, tzinfo=pytz.utc)
        )

        attachment_file_4 = AttachmentFileFactory(
            title='Tracking document 2',
            id=9,
            tag='CR',
            url='http://cr-document.com/9',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url9',
            allegation=allegation_4,
            external_created_at=datetime(2015, 9, 14, 12, 0, 1, tzinfo=pytz.utc)
        )

        AttachmentFileFactory(
            title='Not appear attachment',
            id=10,
            tag='CR',
            url='http://cr-document.com/10',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url10',
            allegation=allegation_4,
            external_created_at=datetime(2015, 6, 13, 12, 0, 1, tzinfo=pytz.utc)
        )

        attachment_file_5 = AttachmentFileFactory(
            title='Tracking document 3',
            id=11,
            tag='CR',
            url='http://cr-document.com/11',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url11',
            allegation=allegation_5,
            external_created_at=datetime(2015, 9, 14, 12, 0, 1, tzinfo=pytz.utc)
        )

        # Should not have this in result because show = False
        AttachmentFileFactory(
            allegation=allegation_1,
            title='CR document 12',
            id=12,
            tag='CR',
            url='http://cr-document.com/12',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url12',
            external_created_at=datetime(2015, 9, 14, 12, 0, 1, tzinfo=pytz.utc),
            show=False
        )

        # Should still count but not 1st row because is attached to a download event
        attachment_file_6 = AttachmentFileFactory(
            title='Attachment not appear because is download event',
            id=13,
            tag='CR',
            url='http://cr-document.com/13',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url13',
            allegation=allegation_4,
            external_created_at=datetime(2015, 7, 13, 12, 0, 1, tzinfo=pytz.utc)
        )
        with freeze_time(datetime(2019, 1, 17, 12, 0, 1, tzinfo=pytz.utc)):
            AttachmentTrackingFactory(attachment_file=attachment_file_3)

        with freeze_time(datetime(2019, 1, 18, 12, 0, 1, tzinfo=pytz.utc)):
            AttachmentTrackingFactory(attachment_file=attachment_file_4)

        with freeze_time(datetime(2019, 1, 12, 12, 0, 1, tzinfo=pytz.utc)):
            AttachmentTrackingFactory(attachment_file=attachment_file_5)

        with freeze_time(datetime(2019, 10, 14, 12, 0, 1, tzinfo=pytz.utc)):
            AttachmentTrackingFactory(
                attachment_file=attachment_file_6,
                kind=constants.DOWNLOAD_EVENT_TYPE)

        allegation_cache_manager.cache_data()

        results = LatestDocumentsQuery.execute(5)

        expected_results = [
            {
                'id': attachment_file_1.id,
                'allegation_id': '123',
                'last_active_at': datetime(2019, 1, 19, 12, 1, 1, tzinfo=pytz.utc),
            },
            {
                'id': attachment_file_4.id,
                'allegation_id': '321',
                'last_active_at': datetime(2019, 1, 18, 12, 0, 1, tzinfo=pytz.utc),
            },
            {
                'id': attachment_file_2.id,
                'allegation_id': '456',
                'last_active_at': datetime(2019, 1, 15, 9, 3, 1, tzinfo=pytz.utc),
            },
            {
                'id': attachment_file_5.id,
                'allegation_id': '987',
                'last_active_at': datetime(2019, 1, 12, 12, 0, 1, tzinfo=pytz.utc),
            },
        ]

        expect(len(results)).to.eq(len(expected_results))
        for index, attachment_data in enumerate(results):
            expected_attachment_data = expected_results[index]
            expect(attachment_data.id).to.eq(expected_attachment_data['id'])
            expect(attachment_data.allegation_id).to.eq(expected_attachment_data['allegation_id'])
            expect(attachment_data.last_active_at).to.eq(expected_attachment_data['last_active_at'])
