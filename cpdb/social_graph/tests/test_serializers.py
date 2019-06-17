import pytz
from datetime import datetime

from django.test import TestCase

from robber import expect

from data.constants import MEDIA_TYPE_DOCUMENT
from data.factories import OfficerFactory, AllegationFactory, AllegationCategoryFactory, AttachmentFileFactory, \
    OfficerAllegationFactory, VictimFactory
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
            allegation=allegation,
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
            sustained_count=2,
            birth_year=1980,
            race='Asian',
            gender='M',
            rank='Police Officer',
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
        # setattr(allegation, 'officerallegation_set', [officer_allegation])

        expect(AllegationSerializer(allegation).data).to.eq({
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
                    'gender': 'Male',
                    'race': 'Asian',
                    'rank': 'Police Officer',
                    'birth_year': 1980,
                    'recommended_outcome': '10 Day Suspension',
                    'final_outcome': 'Separation',
                    'final_finding': 'Sustained',
                    'category': 'Use of Force',
                    'complaint_count': 5,
                    'sustained_count': 2,
                    'complaint_percentile': 85.0,
                    'disciplined': True,
                    'percentile': {
                        'percentile_allegation': '85.0000',
                        'percentile_allegation_civilian': '90.0000',
                        'percentile_allegation_internal': '95.0000',
                        'percentile_trr': '80.0000',
                    },
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
