from django.test import TestCase
from django.urls import reverse

from robber import expect

from toast.factories import ToastFactory


class ToastViewSetTestCase(TestCase):
    def test_list(self):
        ToastFactory(
            name='OFFICER',
            template='**{rank} {full_name}** {age} {race} {gender},'
                     '\nwith *{complaint_count} complaints*, *{sustained_count} sustained* {action_type}.'
        )
        ToastFactory(
            name='CR',
            template='**CR #{crid}** *categorized as {category}*\nhappened in {incident_date} {action_type}.'
        )
        ToastFactory(
            name='TRR',
            template='**TRR #{id}** *categorized as {force_type}*\nhappened in {incident_date} {action_type}.'
        )
        response = self.client.get(reverse('api-v2:toast-list'))
        expect(response.data).to.eq([
            {
                'name': 'OFFICER',
                'template': '**{rank} {full_name}** {age} {race} {gender},'
                            '\nwith *{complaint_count} complaints*, *{sustained_count} sustained* {action_type}.'
            },
            {
                'name': 'CR',
                'template': '**CR #{crid}** *categorized as {category}*\nhappened in {incident_date} {action_type}.'
            },
            {
                'name': 'TRR',
                'template': '**TRR #{id}** *categorized as {force_type}*\nhappened in {incident_date} {action_type}.'
            }
        ])
