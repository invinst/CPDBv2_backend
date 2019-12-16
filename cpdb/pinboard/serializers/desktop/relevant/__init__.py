from .officer_serializer import OfficerSerializer as RelevantOfficerSerializer
from .allegation_serializer import AllegationSerializer as RelevantAllegationSerializer
from .document_serializer import DocumentSerializer as RelevantDocumentSerializer

__all__ = [
    'RelevantOfficerSerializer', 'RelevantAllegationSerializer', 'RelevantDocumentSerializer'
]
