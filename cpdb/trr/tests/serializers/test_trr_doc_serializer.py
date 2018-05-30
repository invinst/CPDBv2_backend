from datetime import datetime

from django.test import TestCase

from robber import expect

from trr.serializers.trr_doc_serializers import TRRDocSerializer
from trr.factories import (TRRFactory, ActionResponseFactory)


class TRRDocSerializerTestCase(TestCase):
    def test_get_subject_gender(self):
        trr = TRRFactory(subject_gender='M')

        result = TRRDocSerializer(trr).data
        expect(result['subject_gender']).to.eq('Male')

    def test_get_subject_gender_other_gender(self):
        trr = TRRFactory(subject_gender='A')

        result = TRRDocSerializer(trr).data
        expect(result['subject_gender']).to.eq('A')

    def test_get_address(self):
        trr = TRRFactory(block='34XX', street='Douglas Blvd')
        result = TRRDocSerializer(trr).data
        expect(result['address']).to.eq('34XX Douglas Blvd')

    def test_get_address_missing_data(self):
        trr_no_street = TRRFactory(block='34XX', street=None)
        trr_no_block = TRRFactory(block=None, street='Douglas Blvd')
        trr_no_address = TRRFactory(block=None, street=None)

        expect(TRRDocSerializer(trr_no_street).data['address']).to.eq('34XX')
        expect(TRRDocSerializer(trr_no_block).data['address']).to.eq('Douglas Blvd')
        expect(TRRDocSerializer(trr_no_address).data['address']).to.eq('')

    def test_get_date_of_incident(self):
        trr = TRRFactory(trr_datetime=datetime(2012, 1, 23))
        expect(TRRDocSerializer(trr).data['date_of_incident']).to.eq('2012-01-23')

    def test_get_actions(self):
        trr = TRRFactory()
        ActionResponseFactory(trr=trr, action='TAKE DOWN/EMERGENCY HANDCUFFING')
        ActionResponseFactory(trr=trr, action='Armbar')
        ActionResponseFactory(trr=trr, action='Member Presence')
        ActionResponseFactory(trr=trr, action='other (specify)')

        expect(TRRDocSerializer(trr).data['actions']).to.eq([
            'Other (Specify)',
            'Member Presence',
            'Armbar',
            'Take Down/Emergency Handcuffing'
        ])
