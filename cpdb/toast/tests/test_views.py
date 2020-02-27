from django.test import TestCase
from django.urls import reverse

from robber import expect

from toast.factories import ToastFactory


class ToastDesktopViewSet(TestCase):
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
        expect(response.data).to.eq([{
            'name': 'OFFICER',
            'template': '**{rank} {full_name}** {age} {race} {gender},'
                        '\nwith *{complaint_count} complaints*, *{sustained_count} sustained* {action_type}.'
        }, {
            'name': 'CR',
            'template': '**CR #{crid}** *categorized as {category}*\nhappened in {incident_date} {action_type}.'
        }, {
            'name': 'TRR',
            'template': '**TRR #{id}** *categorized as {force_type}*\nhappened in {incident_date} {action_type}.'
        }])


class ToastMobileViewSet(TestCase):
    def test_list(self):
        ToastFactory(
            name='MOBILE OFFICER',
            template='{full_name} {action_type} pinboard'
        )
        ToastFactory(
            name='MOBILE CR',
            template='CR #{crid} {action_type} pinboard'
        )
        ToastFactory(
            name='MOBILE TRR',
            template='TRR #{id} {action_type} pinboard'
        )
        response = self.client.get(reverse('api-v2:toast-mobile-list'))
        expect(response.data).to.eq([{
            'name': 'OFFICER',
            'template': '{full_name} {action_type} pinboard'
        }, {
            'name': 'CR',
            'template': 'CR #{crid} {action_type} pinboard'
        }, {
            'name': 'TRR',
            'template': 'TRR #{id} {action_type} pinboard'
        }])
