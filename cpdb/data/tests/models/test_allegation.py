from datetime import datetime, timedelta

import pytz
from django.test.testcases import TestCase
from django.utils.timezone import now

from robber.expect import expect
from freezegun import freeze_time

from analytics.factories import AttachmentTrackingFactory
from data.constants import MEDIA_TYPE_DOCUMENT, MEDIA_TYPE_AUDIO, MEDIA_TYPE_VIDEO
from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, ComplainantFactory,
    AllegationCategoryFactory, AttachmentFileFactory
)
from data.models import Allegation


class AllegationTestCase(TestCase):
    def test_address(self):
        allegation = AllegationFactory(add1='3000', add2='Michigan Ave', city='Chicago IL')
        allegation1 = AllegationFactory(add1='', add2='', city='')
        allegation2 = AllegationFactory(add1='', add2=' ', city='')

        expect(allegation.address).to.eq('3000 Michigan Ave, Chicago IL')
        expect(allegation1.address).to.eq('')
        expect(allegation2.address).to.eq('')

    def test_address_missing_sub_address(self):
        allegation = AllegationFactory(add1='', add2='', city='')
        expect(allegation.address).to.eq('')
        allegation = AllegationFactory(add1='15', add2='', city='')
        expect(allegation.address).to.eq('15')
        allegation = AllegationFactory(add1='', add2='abc', city='')
        expect(allegation.address).to.eq('abc')
        allegation = AllegationFactory(add1='', add2='', city='Chicago')
        expect(allegation.address).to.eq('Chicago')
        allegation = AllegationFactory(add1='15', add2='abc', city='')
        expect(allegation.address).to.eq('15 abc')
        allegation = AllegationFactory(add1='15', add2='', city='Chicago')
        expect(allegation.address).to.eq('15, Chicago')
        allegation = AllegationFactory(add1='', add2='abc', city='Chicago')
        expect(allegation.address).to.eq('abc, Chicago')

    def test_address_old_complaint_address(self):
        allegation = AllegationFactory(old_complaint_address='3XX W. 58TH ST.')
        expect(allegation.address).to.eq('3XX W. 58TH ST.')

    def test_officer_allegations(self):
        allegation = AllegationFactory()
        OfficerAllegationFactory(id=1, allegation=allegation, officer=OfficerFactory())
        expect(allegation.officer_allegations.count()).to.eq(1)
        expect(allegation.officer_allegations[0].id).to.eq(1)

    def test_complainants(self):
        allegation = AllegationFactory()
        ComplainantFactory(id=1, allegation=allegation)
        expect(allegation.complainants.count()).to.eq(1)
        expect(allegation.complainants[0].id).to.eq(1)

    def test_get_category_names(self):
        allegation = AllegationFactory()

        category1 = AllegationCategoryFactory(category='Use of Force')
        category2 = AllegationCategoryFactory(category='Illegal Search')
        OfficerAllegationFactory(allegation=allegation, allegation_category=category1)
        OfficerAllegationFactory(allegation=allegation, allegation_category=category2)
        expect(allegation.category_names).to.eq(['Illegal Search', 'Use of Force'])

        OfficerAllegationFactory(allegation=allegation, allegation_category=None)
        expect(allegation.category_names).to.eq(['Illegal Search', 'Unknown', 'Use of Force'])

    def test_complainant_races(self):
        allegation = AllegationFactory()
        ComplainantFactory(race='White', allegation=allegation)
        expect(allegation.complainant_races).to.eq(['White'])

        ComplainantFactory(race='White/Hispinic', allegation=allegation)
        expect(allegation.complainant_races).to.eq(['White', 'White/Hispinic'])

    def test_complainant_age_groups(self):
        allegation = AllegationFactory()
        ComplainantFactory(age=32, allegation=allegation)
        expect(allegation.complainant_age_groups).to.eq(['31-40'])

        ComplainantFactory(age=38, allegation=allegation)
        expect(allegation.complainant_age_groups).to.eq(['31-40'])

        ComplainantFactory(age=55, allegation=allegation)
        expect(allegation.complainant_age_groups).to.eq(['31-40', '51+'])

        allegation_no_complainant = AllegationFactory()
        expect(allegation_no_complainant.complainant_age_groups).to.eq(['Unknown'])

    def test_complainant_genders(self):
        allegation = AllegationFactory()
        ComplainantFactory(gender='F', allegation=allegation)
        expect(allegation.complainant_genders).to.eq(['Female'])

        ComplainantFactory(gender='U', allegation=allegation)
        expect(allegation.complainant_genders).to.eq(['Female', 'Unknown'])

    def test_v2_to_with_officer(self):
        allegation = AllegationFactory(crid='456')
        officer = OfficerFactory(id=123)
        OfficerAllegationFactory(allegation=allegation, officer=officer)

        expect(allegation.v2_to).to.eq('/complaint/456/123/')

    def test_v2_to_without_officer(self):
        allegation = AllegationFactory(crid='456')

        expect(allegation.v2_to).to.eq('/complaint/456/')

    def test_v2_to_with_officerallegation_without_officer(self):
        allegation = AllegationFactory(crid='456')
        OfficerAllegationFactory(allegation=allegation, officer=None)

        expect(allegation.v2_to).to.eq('/complaint/456/')

    def test_documents(self):
        allegation = AllegationFactory()
        attachment1 = AttachmentFileFactory(allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT)
        attachment2 = AttachmentFileFactory(allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT)
        expect(allegation.documents).to.contain(attachment1, attachment2)

    def test_filtered_attachment_files(self):
        allegation = AllegationFactory()
        attachment1 = AttachmentFileFactory(tag='Other', allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT)
        AttachmentFileFactory(tag='OCIR', allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT)
        AttachmentFileFactory(tag='AR', allegation=allegation, file_type=MEDIA_TYPE_DOCUMENT)
        expect(list(allegation.filtered_attachment_files)).to.eq([attachment1])

    def test_get_cr_with_new_documents(self):
        three_month_ago = now() - timedelta(weeks=12)
        allegation_1 = AllegationFactory(crid='123')
        allegation_2 = AllegationFactory(crid='456')
        allegation_3 = AllegationFactory(crid='789')
        allegation_4 = AllegationFactory(crid='321')

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

        with freeze_time(datetime(2018, 8, 14, 12, 0, 1, tzinfo=pytz.utc)):
            AttachmentTrackingFactory(attachment_file=attachment_file_3)

        with freeze_time(datetime(2018, 9, 14, 12, 0, 1, tzinfo=pytz.utc)):
            AttachmentTrackingFactory(attachment_file=attachment_file_4)

        results = Allegation.get_cr_with_new_documents(5)

        expect(len(results)).to.eq(3)

        first_result = results[0]
        expect(first_result.crid).to.eq('321')
        expect(first_result.latest_document_created_at).to.be.none()
        expect(first_result.latest_document_viewed_at).to.eq(datetime(2018, 9, 14, 12, 0, 1, tzinfo=pytz.utc))
        expect(first_result.num_recent_documents).to.eq(0)
        expect(first_result.latest_viewed_documents).to.eq([attachment_file_4])

        second_result = results[1]
        expect(second_result.crid).to.eq('123')
        expect(second_result.latest_document_created_at).to.eq(three_month_ago + timedelta(days=10))
        expect(second_result.latest_document_viewed_at).to.be.none()
        expect(second_result.num_recent_documents).to.eq(2)
        expect(second_result.latest_viewed_documents).to.eq([attachment_file_1])

        third_result = results[2]
        expect(third_result.crid).to.eq('456')
        expect(third_result.latest_document_created_at).to.eq(three_month_ago + timedelta(days=6))
        expect(third_result.latest_document_viewed_at).to.be.none()
        expect(third_result.num_recent_documents).to.eq(1)
        expect(third_result.latest_viewed_documents).to.eq([attachment_file_2])

    def test_get_cr_with_new_documents_no_latest_document_viewed(self):
        three_month_ago = now() - timedelta(weeks=12)
        allegation_1 = AllegationFactory(crid='123')
        allegation_2 = AllegationFactory(crid='456')
        allegation_3 = AllegationFactory(crid='789')
        allegation_4 = AllegationFactory(crid='321')

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

        AttachmentFileFactory(
            title='CR document 9',
            id=9,
            tag='CR',
            url='http://cr-document.com/9',
            file_type=MEDIA_TYPE_DOCUMENT,
            preview_image_url='http://preview.com/url9',
            allegation=allegation_4,
            external_created_at=datetime(2010, 9, 14, 12, 0, 1, tzinfo=pytz.utc)
        )

        results = Allegation.get_cr_with_new_documents(5)

        expect(len(results)).to.eq(3)

        first_result = results[0]
        expect(first_result.crid).to.eq('789')
        expect(first_result.latest_document_created_at).to.eq(three_month_ago + timedelta(days=12))
        expect(first_result.latest_document_viewed_at).to.be.none()
        expect(first_result.num_recent_documents).to.eq(1)
        expect(first_result.latest_viewed_documents).to.eq([attachment_file_3])

        second_result = results[1]
        expect(second_result.crid).to.eq('123')
        expect(second_result.latest_document_created_at).to.eq(three_month_ago + timedelta(days=10))
        expect(second_result.latest_document_viewed_at).to.be.none()
        expect(second_result.num_recent_documents).to.eq(2)
        expect(second_result.latest_viewed_documents).to.eq([attachment_file_1])

        third_result = results[2]
        expect(third_result.crid).to.eq('456')
        expect(third_result.latest_document_created_at).to.eq(three_month_ago + timedelta(days=6))
        expect(third_result.latest_document_viewed_at).to.be.none()
        expect(third_result.num_recent_documents).to.eq(1)
        expect(third_result.latest_viewed_documents).to.eq([attachment_file_2])
