from .officer_serializer import OfficerMobileSerializer as RelevantOfficerMobileSerializer
from .allegation_serializer import AllegationMobileSerializer as RelevantAllegationMobileSerializer
from .document_serializer import DocumentSerializer as RelevantDocumentMobileSerializer

__all__ = [
    'RelevantOfficerMobileSerializer',
    'RelevantAllegationMobileSerializer',
    'RelevantDocumentMobileSerializer',
]
