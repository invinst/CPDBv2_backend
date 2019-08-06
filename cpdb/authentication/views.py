from django.contrib.auth import get_user_model

from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response

from authentication.utils import send_forgot_password_email

User = get_user_model()


class UserViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], url_path='sign-in', url_name='sign-in')
    def sign_in(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({
                'message': "Sorry, You've entered an incorrect name."
                }, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({
                'message': "You've entered an incorrect password."
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'apiAccessToken': token.key
                }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='forgot-password', url_name='forgot-password')
    def password_reset(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
            send_forgot_password_email(request, user)
        except User.DoesNotExist:
            return Response({
                'message': "Sorry, there's no account registered with this email address."
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': "Please check your email for a password reset link."
            }, status=status.HTTP_200_OK)
