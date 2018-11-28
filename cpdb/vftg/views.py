from rest_framework import viewsets, status
from rest_framework.response import Response

from vftg.mailchimp_service import MailchimpService, MailchimpAPIError


class VFTGViewSet(viewsets.ViewSet):
    def create(self, request):
        try:
            MailchimpService.subscribe(request.data['email'])
        except MailchimpAPIError as e:
            return Response({'success': False, 'detail': e.value}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': True})
