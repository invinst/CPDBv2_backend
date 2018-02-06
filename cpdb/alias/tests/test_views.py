from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from robber import expect

from search.tests.utils import IndexMixin
from authentication.factories import AdminUserFactory
from data.factories import OfficerFactory
from search.doc_types import OfficerDocType


class AliasViewSetTestCase(IndexMixin, APITestCase):
    def setUp(self):
        super(AliasViewSetTestCase, self).setUp()
        self.officer = OfficerFactory(id=1)
        self.officer_doc = OfficerDocType(meta={'id': '1'})
        self.officer_doc.save()
        self.refresh_index()

        admin_user = AdminUserFactory()
        token, _ = Token.objects.get_or_create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_update_officer_aliases(self):
        response = self.client.put(
            reverse('api-v2:alias-detail', kwargs={'alias_type': 'officer', 'pk': '1'}),
            {
                'aliases': ['foo', 'bar']
            }
        )

        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({'message': 'Aliases successfully updated', 'aliases': ['foo', 'bar']})

    def test_update_with_invalid_aliases(self):
        response = self.client.put(
            reverse('api-v2:alias-detail', kwargs={'alias_type': 'officer', 'pk': '1'}),
            {
                'aliases': ['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']
            }
        )

        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data).to.eq({'message': {'aliases': ['Ensure this field has no more than 20 characters.']}})

    def test_update_aliases_with_wrong_type(self):

        response = self.client.put(
            reverse('api-v2:alias-detail', kwargs={'alias_type': 'not an alias type', 'pk': '1'}),
            {
                'aliases': ['foo', 'bar']
            }
        )

        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)
        expect(response.data).to.eq({'message': 'Cannot find type "not an alias type"'})

    def test_update_aliases_with_wrong_pk(self):

        response = self.client.put(
            reverse('api-v2:alias-detail', kwargs={'alias_type': 'officer', 'pk': '2'}),
            {
                'aliases': ['foo', 'bar']
            }
        )

        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)
        expect(response.data).to.eq({'message': 'Cannot find any "officer" record with pk=2'})
