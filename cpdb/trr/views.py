from copy import deepcopy

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from email_service.constants import TRR_ATTACHMENT_REQUEST
from email_service.service import send_attachment_request_email
from trr.models import TRR
from trr.serializers.trr_response_serializers import TRRSerializer, AttachmentRequestSerializer


class TRRDesktopViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        trr = get_object_or_404(TRR, id=pk)
        return Response(TRRSerializer(trr).data)

    @action(detail=True, methods=['POST'], url_path='request-document')
    def request_document(self, request, pk):
        trr = get_object_or_404(TRR, id=pk)
        data = deepcopy(request.data)
        data['trr'] = trr.pk
        serializer = AttachmentRequestSerializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            send_attachment_request_email(data['email'], attachment_type=TRR_ATTACHMENT_REQUEST, pk=pk)
            return Response({'message': 'Thanks for subscribing', 'trr_id': int(pk)})

        except ValidationError as e:
            if e.get_codes() == {'non_field_errors': ['unique']}:
                return Response({'message': 'Email already added', 'trr_id': int(pk)})

            return Response({'message': 'Please enter a valid email'}, status=status.HTTP_400_BAD_REQUEST)


class TRRMobileViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        trr = get_object_or_404(TRR, id=pk)
        return Response(TRRSerializer(trr).data)

    @action(detail=True, methods=['POST'], url_path='request-document')
    def request_document(self, request, pk):
        trr = get_object_or_404(TRR, id=pk)
        data = deepcopy(request.data)
        data['trr'] = trr.pk
        serializer = AttachmentRequestSerializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            send_attachment_request_email(data['email'], attachment_type=TRR_ATTACHMENT_REQUEST, pk=pk)
            return Response({'message': 'Thanks for subscribing', 'trr_id': int(pk)})

        except ValidationError as e:
            if e.get_codes() == {'non_field_errors': ['unique']}:
                return Response(
                    {'message': 'Email already added', 'trr_id': int(pk)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({'message': 'Please enter a valid email'}, status=status.HTTP_400_BAD_REQUEST)
