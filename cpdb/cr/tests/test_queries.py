from datetime import datetime, timedelta

import pytz
from django.test.testcases import TestCase
from django.utils.timezone import now

from robber.expect import expect
from freezegun import freeze_time

from analytics import constants
from analytics.factories import AttachmentTrackingFactory
from data.constants import MEDIA_TYPE_DOCUMENT, MEDIA_TYPE_AUDIO, MEDIA_TYPE_VIDEO
from data.factories import AllegationFactory, AttachmentFileFactory
from cr.queries import LatestDocumentsQuery


class LatestDocumentsQueryTestCase(TestCase):
    def test_execute(self):
        three_month_ago = now() - timedelta(weeks=12)
        allegation_1 = AllegationFactory(crid='123')
        allegation_2 = AllegationFactory(crid='456')
        allegation_3 = AllegationFactory(crid='789')
        allegation_4 = AllegationFactory(crid='321')
        allegation_5 = AllegationFactory(crid='987')

        attachment_file_1 = AttachmentFileFactory(
            allegation=allegation_1,
            title='CR document 1',
            id=1,
            tag='CR',
            url='http://cr-document.com/1',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url1',
            external_created_at=three_month_ago + timedelta(days=10)
        )
        AttachmentFileFactory(
            allegation=allegation_1,
            title='CR document 2',
            id=2,
            tag='CR',
            url='http://cr-document.com/2',
            file_type=MEDIA_TYPE_DOCUMENT,
            external_created_at=three_month_ago + timedelta(days=5)
        )

        attachment_file_2 = AttachmentFileFactory(
            allegation=allegation_2,
            title='CR document 3',
            id=3,
            tag='CR',
            url='http://cr-document.com/3',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url3',
            external_created_at=three_month_ago + timedelta(days=6)
        )

        AttachmentFileFactory(
            allegation=allegation_2,
            title='CR document 4',
            id=4,
            tag='OCIR',
            url='http://cr-document.com/4',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url4',
            external_created_at=three_month_ago + timedelta(days=10)
        )

        AttachmentFileFactory(
            allegation=allegation_2,
            title='CR document 5',
            id=5,
            tag='AR',
            url='http://cr-document.com/5',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url5',
            external_created_at=three_month_ago + timedelta(days=11)
        )

        AttachmentFileFactory(
            allegation=allegation_3,
            title='CR document 6',
            id=6,
            tag='CR',
            url='http://cr-document.com/6',
            file_type=MEDIA_TYPE_AUDIO,
            preview_image_url='http://preview.com/url6',
            external_created_at=three_month_ago + timedelta(days=12)
        )

        AttachmentFileFactory(
            allegation=allegation_3,
            title='CR document 7',
            id=7,
            tag='CR',
            url='http://cr-document.com/7',
            file_type=MEDIA_TYPE_VIDEO,
            preview_image_url='http://preview.com/url7',
            external_created_at=three_month_ago + timedelta(days=13)
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
            external_created_at=three_month_ago + timedelta(days=15),
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

        with freeze_time(datetime(2018, 8, 14, 12, 0, 1, tzinfo=pytz.utc)):
            AttachmentTrackingFactory(attachment_file=attachment_file_3)

        with freeze_time(datetime(2018, 9, 14, 12, 0, 1, tzinfo=pytz.utc)):
            AttachmentTrackingFactory(attachment_file=attachment_file_4)

        with freeze_time(datetime(2018, 7, 14, 12, 0, 1, tzinfo=pytz.utc)):
            AttachmentTrackingFactory(attachment_file=attachment_file_5)

        with freeze_time(datetime(2018, 10, 14, 12, 0, 1, tzinfo=pytz.utc)):
            AttachmentTrackingFactory(
                attachment_file=attachment_file_6,
                kind=constants.DOWNLOAD_EVENT_TYPE)

        results = LatestDocumentsQuery.execute(5)

        expect(len(results)).to.eq(4)

        first_result = results[0]
        expect(first_result.id).to.eq(attachment_file_4.id)
        expect(first_result.allegation_id).to.eq('321')
        expect(first_result.latest_viewed_at).to.eq(datetime(2018, 9, 14, 12, 0, 1, tzinfo=pytz.utc))
        expect(first_result.num_recent_documents).to.eq(1)

        second_result = results[1]
        expect(second_result.id).to.eq(attachment_file_5.id)
        expect(second_result.allegation_id).to.eq('987')
        expect(second_result.latest_viewed_at).to.eq(datetime(2018, 7, 14, 12, 0, 1, tzinfo=pytz.utc))
        expect(second_result.num_recent_documents).to.eq(1)

        third_result = results[2]
        expect(third_result.id).to.eq(attachment_file_1.id)
        expect(third_result.allegation_id).to.eq('123')
        expect(third_result.latest_viewed_at).to.be.none()
        expect(third_result.num_recent_documents).to.eq(2)

        fourth_result = results[3]
        expect(fourth_result.id).to.eq(attachment_file_2.id)
        expect(fourth_result.allegation_id).to.eq('456')
        expect(fourth_result.latest_viewed_at).to.be.none()
        expect(fourth_result.num_recent_documents).to.eq(1)

    def test_execute_with_no_latest_viewed(self):
        three_month_ago = now() - timedelta(weeks=12)
        allegation_1 = AllegationFactory(crid='123')
        allegation_2 = AllegationFactory(crid='456')
        allegation_3 = AllegationFactory(crid='789')

        attachment_file_1 = AttachmentFileFactory(
            allegation=allegation_1,
            title='CR document 1',
            id=1,
            tag='CR',
            url='http://cr-document.com/1',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url1',
            external_created_at=three_month_ago + timedelta(days=10)
        )
        AttachmentFileFactory(
            allegation=allegation_1,
            title='CR document 2',
            id=2,
            tag='CR',
            url='http://cr-document.com/2',
            file_type=MEDIA_TYPE_DOCUMENT,
            external_created_at=three_month_ago + timedelta(days=5)
        )

        attachment_file_2 = AttachmentFileFactory(
            allegation=allegation_2,
            title='CR document 3',
            id=3,
            tag='CR',
            url='http://cr-document.com/3',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url3',
            external_created_at=three_month_ago + timedelta(days=6)
        )

        AttachmentFileFactory(
            allegation=allegation_2,
            title='CR document 4',
            id=4,
            tag='OCIR',
            url='http://cr-document.com/4',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url4',
            external_created_at=three_month_ago + timedelta(days=10)
        )

        AttachmentFileFactory(
            allegation=allegation_2,
            title='CR document 5',
            id=5,
            tag='AR',
            url='http://cr-document.com/5',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url5',
            external_created_at=three_month_ago + timedelta(days=11)
        )

        attachment_file_3 = AttachmentFileFactory(
            allegation=allegation_3,
            title='CR document 6',
            id=6,
            tag='CR',
            url='http://cr-document.com/6',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url6',
            external_created_at=three_month_ago + timedelta(days=12)
        )

        AttachmentFileFactory(
            allegation=allegation_3,
            title='CR document 7',
            id=7,
            tag='CR',
            url='http://cr-document.com/7',
            file_type=MEDIA_TYPE_AUDIO,
            preview_image_url='http://preview.com/url7',
            external_created_at=three_month_ago + timedelta(days=13)
        )

        AttachmentFileFactory(
            allegation=allegation_3,
            title='CR document 8',
            id=8,
            tag='CR',
            url='http://cr-document.com/8',
            file_type=MEDIA_TYPE_VIDEO,
            preview_image_url='http://preview.com/url8',
            external_created_at=three_month_ago + timedelta(days=14)
        )

        results = LatestDocumentsQuery.execute(5)

        expect(len(results)).to.eq(3)

        first_result = results[0]
        expect(first_result.id).to.eq(attachment_file_3.id)
        expect(first_result.allegation_id).to.eq('789')
        expect(first_result.latest_viewed_at).to.be.none()
        expect(first_result.num_recent_documents).to.eq(1)

        second_result = results[1]
        expect(second_result.id).to.eq(attachment_file_1.id)
        expect(second_result.allegation_id).to.eq('123')
        expect(second_result.latest_viewed_at).to.be.none()
        expect(second_result.num_recent_documents).to.eq(2)

        third_result = results[2]
        expect(third_result.id).to.eq(attachment_file_2.id)
        expect(third_result.allegation_id).to.eq('456')
        expect(third_result.latest_viewed_at).to.be.none()
        expect(third_result.num_recent_documents).to.eq(1)
