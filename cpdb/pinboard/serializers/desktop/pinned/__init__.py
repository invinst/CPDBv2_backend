from .officer_serializer import OfficerSerializer as PinnedOfficerSerializer
from .allegation_serializer import AllegationSerializer as PinnedAllegationSerializer
from .trr_serializer import TRRSerializer as PinnedTRRSerializer

__all__ = [
    'PinnedOfficerSerializer', 'PinnedAllegationSerializer', 'PinnedTRRSerializer'
]
