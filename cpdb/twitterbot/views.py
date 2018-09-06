import hmac

from django.conf import settings

from rest_framework import viewsets, status
from rest_framework.response import Response

from twitterbot.utils.cryptography import get_hash_token
from twitterbot.workers import ActivityEventWorker


class WebhookViewSet(viewsets.ViewSet):
    def list(self, request):
        """
        GET: Twitter Challenge Response Check (CRC)
        """
        crc_token = request.GET.get('crc_token')
        if crc_token:
            hash_token = get_hash_token(
                key=settings.TWITTER_CONSUMER_SECRET,
                msg=crc_token
            )
            response = {
                'response_token': hash_token
            }

            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Error: crc_token is missing from request'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        """
        POST: Webhook to receive subscribed account's activity events from Twitter
        """
        twitter_signature = request.META.get('HTTP_X_TWITTER_WEBHOOKS_SIGNATURE', '')
        request_hash_token = get_hash_token(
            key=settings.TWITTER_CONSUMER_SECRET,
            msg=request.body
        )

        if hmac.compare_digest(twitter_signature, request_hash_token):
            ActivityEventWorker().process(request.data)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Cannot recognize the requesting source'}, status=status.HTTP_400_BAD_REQUEST)
