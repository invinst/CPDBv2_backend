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
)
from social_graph.serializers.allegation_serializer import AllegationSerializer


class AllegationSerializerTestCase(TestCase):
    def test_serialization(self):
        category = AllegationCategoryFactory(category='Use of Force', allegation_name='Subcategory')
        allegation = AllegationFactory(
            crid='123',
            is_officer_complaint=True,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc),
            most_common_category=category,
        )
        attachment = AttachmentFileFactory(
            tag='TRR',
            allegation=allegation,
            title='CR document',
            id='123456',
            url='http://cr-document.com/',
            file_type=MEDIA_TYPE_DOCUMENT
        )
        officer = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_allegation = OfficerAllegationFactory(officer=officer)

        setattr(allegation, 'prefetch_filtered_attachment_files', [attachment])
        allegation.officerallegation_set.set([officer_allegation])

        expect(AllegationSerializer(allegation).data).to.eq({
            'crid': '123',
            'incident_date': '2005-12-31',
            'most_common_category': {
                'category': 'Use of Force',
                'allegation_name': 'Subcategory',
            },
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
