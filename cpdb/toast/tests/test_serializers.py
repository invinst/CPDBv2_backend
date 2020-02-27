from django.test import TestCase
from robber import expect

from toast.serializers import ToastDesktopSerializer, ToastMobileSerializer
from toast.factories import ToastFactory


class ToastDesktopSerializerTestCase(TestCase):
    def test_serialization(self):
        toast = ToastFactory(
            name='CR',
            template='**CR #{crid}** *categorized as {category}*\nhappened in {incident_date} {action_type}.'
        )

        expect(ToastDesktopSerializer(toast).data).to.eq({
            'name': 'CR',
            'template': '**CR #{crid}** *categorized as {category}*\nhappened in {incident_date} {action_type}.'
        })


class ToastMobileSerializerTestCase(TestCase):
    def test_serialization(self):
        toast = ToastFactory(
            name='MOBILE CR',
            template='CR #{crid} {action_type} pinboard'
        )

        expect(ToastMobileSerializer(toast).data).to.eq({
            'name': 'CR',
            'template': 'CR #{crid} {action_type} pinboard'
        })
