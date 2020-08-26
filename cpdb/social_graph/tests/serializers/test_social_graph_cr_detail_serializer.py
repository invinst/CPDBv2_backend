import pytz
from datetime import datetime

from django.test import TestCase

from robber import expect

from data.constants import MEDIA_TYPE_DOCUMENT
from data.factories import (
    AllegationFactory,
    AllegationCategoryFactory,
    AttachmentFileFactory,
    OfficerFactory,
    OfficerAllegationFactory,
    VictimFactory,
)
from social_graph.serializers import SocialGraphCRDetailSerializer


class SocialGraphCRDetailSerializerTestCase(TestCase):
    def test_serialization(self):
        category = AllegationCategoryFactory(category='Use of Force', allegation_name='Improper Search Of Person')
        allegation = AllegationFactory(
            crid='123',
            is_officer_complaint=True,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc),
            most_common_category=category,
            old_complaint_address='34XX Douglas Blvd',
        )
        attachment = AttachmentFileFactory(
            tag='TRR',
            owner=allegation,
            title='CR document',
            id='123456',
            url='http://cr-document.com/',
            file_type=MEDIA_TYPE_DOCUMENT
        )
        officer = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=5,
            trr_percentile=80,
            complaint_percentile=85,
            civilian_allegation_percentile=90,
            internal_allegation_percentile=95
        )
        officer_allegation = OfficerAllegationFactory(
            id=1,
            officer=officer,
            allegation=allegation,
            recc_outcome='10 Day Suspension',
            final_finding='SU',
            final_outcome='Separation',
            disciplined=True,
            allegation_category=category
        )
        VictimFactory(
            gender='M',
            race='Black',
            age=35,
            allegation=allegation
        )

        setattr(allegation, 'prefetch_filtered_attachment_files', [attachment])
        allegation.officerallegation_set.set([officer_allegation])

        expect(SocialGraphCRDetailSerializer(allegation).data).to.eq({
            'kind': 'CR',
            'crid': '123',
            'to': '/complaint/123/',
            'category': 'Use of Force',
            'subcategory': 'Improper Search Of Person',
            'incident_date': '2005-12-31',
            'address': '34XX Douglas Blvd',
            'victims': [
                {
                    'gender': 'Male',
                    'race': 'Black',
                    'age': 35
                }
            ],
            'coaccused': [
                {
                    'id': 8562,
                    'full_name': 'Jerome Finnigan',
                    'allegation_count': 5,
                    'percentile_allegation': '85.0000',
                    'percentile_allegation_civilian': '90.0000',
                    'percentile_allegation_internal': '95.0000',
                    'percentile_trr': '80.0000',
                }
            ],
            'attachments': [
                {
                    'id': '123456',
                    'title': 'CR document',
                    'url': 'http://cr-document.com/',
                    'file_type': MEDIA_TYPE_DOCUMENT,
                }
            ],
            'officer_ids': [8562],
        })
