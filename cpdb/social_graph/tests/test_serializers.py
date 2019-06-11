import pytz
from datetime import datetime

from django.test import TestCase

from robber import expect

from data.constants import MEDIA_TYPE_DOCUMENT
from data.factories import OfficerFactory, AllegationFactory, AllegationCategoryFactory, AttachmentFileFactory, \
    OfficerAllegationFactory
from social_graph.serializers import OfficerSerializer, OfficerDetailSerializer, AllegationSerializer, \
    AccussedSerializer


class OfficerSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
        )

        expect(OfficerSerializer(officer).data).to.eq({
            'id': 8562,
            'full_name': 'Jerome Finnigan',
            'percentile': {
                'percentile_allegation_civilian': '1.1000',
                'percentile_allegation_internal': '2.2000',
                'percentile_trr': '3.3000'
            }
        })


class OfficerDetailSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(
            id=8562,
            first_name='Jerome',
            last_name='Finnigan',
            rank='Police Officer',
            current_badge='123',
            race='White',
            birth_year='1972',
            gender='M',
            allegation_count=1,
            sustained_count=1,
            honorable_mention_count=1,
            major_award_count=1,
            trr_count=1,
            discipline_count=1,
            civilian_compliment_count=1,
            appointed_date='1976-06-10',
            civilian_allegation_percentile=1.1,
            internal_allegation_percentile=2.2,
            trr_percentile=3.3,
        )

        expect(OfficerDetailSerializer(officer).data).to.eq({
            'id': 8562,
            'full_name': 'Jerome Finnigan',
            'rank': 'Police Officer',
            'badge': '123',
            'race': 'White',
            'birth_year': '1972',
            'gender': 'M',
            'allegation_count': 1,
            'sustained_count': 1,
            'honorable_mention_count': 1,
            'major_award_count': 1,
            'trr_count': 1,
            'discipline_count': 1,
            'civilian_compliment_count': 1,
            'appointed_date': '1976-06-10',
            'percentile': {
                'percentile_allegation_civilian': '1.1000',
                'percentile_allegation_internal': '2.2000',
                'percentile_trr': '3.3000',
            }
        })


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
        # setattr(allegation, 'officerallegation_set', [officer_allegation])

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


class AccussedSerializerTestCase(TestCase):
    def test_serialization(self):
        class Accused(object):
            def __init__(self, officer_id_1, officer_id_2, incident_date, accussed_count):
                self.officer_id_1 = officer_id_1
                self.officer_id_2 = officer_id_2
                self.incident_date = incident_date
                self.accussed_count = accussed_count

        accused = Accused(
            officer_id_1=1,
            officer_id_2=2,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc),
            accussed_count=3,
        )

        expect(AccussedSerializer(accused).data).to.eq({
            'officer_id_1': 1,
            'officer_id_2': 2,
            'incident_date': '2005-12-31',
            'accussed_count': 3,
        })
