from django.test import TestCase
from robber import expect

from toast.serializers import ToastSerializer
from toast.factories import ToastFactory


class ToastSerialierTestCase(TestCase):
    def test_serialization(self):
        toast = ToastFactory(
            name='CR',
            template='**CR #{crid}** *categorized as {category}*\nhappened in {incident_date} {action_type}.'
        )

        expect(ToastSerializer(toast).data).to.eq({
            'name': 'CR',
            'template': '**CR #{crid}** *categorized as {category}*\nhappened in {incident_date} {action_type}.'
        })
