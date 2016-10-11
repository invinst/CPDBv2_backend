from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.core import mail

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from authentication.factories import AdminUserFactory

User = get_user_model()


class AuthenticationAPITestCase(APITestCase):
    def test_sign_in(self):
        user = AdminUserFactory(raw_password='abc@123')
        response = self.client.post(reverse('api:user-sign-in'), {
            'username': user.username,
            'password': 'abc@123'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['apiAccessToken'], Token.objects.get(user=user).key)

    def test_sign_in_wrong_username(self):
        response = self.client.post(reverse('api:user-sign-in'), {
            'username': 'non_existing_user_name',
            'password': 'edf@123'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Sorry, You've entered an incorrect name.")

    def test_sign_in_wrong_password(self):
        user = AdminUserFactory(raw_password='abc@123')
        response = self.client.post(reverse('api:user-sign-in'), {
            'username': user.username,
            'password': 'def@123'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "You've entered an incorrect password.")

    def test_forgot_password(self):
        AdminUserFactory(email='abc@test.com')
        response = self.client.post(reverse('api:user-forgot-password'), {
            'email': 'abc@test.com'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Please check your email for a password reset link.")

        last_message = mail.outbox[-1]
        self.assertEqual(last_message.subject, 'Password reset on testserver')

    def test_forgot_password_wrong_email(self):
        response = self.client.post(reverse('api:user-forgot-password'), {
            'email': 'nonexisting@email.com'
            })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Sorry, there's no account registered with this email address.")
