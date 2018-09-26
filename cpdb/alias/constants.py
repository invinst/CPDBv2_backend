from data.models import Officer, Area, PoliceUnit
from officers.doc_types import OfficerInfoDocType
from search.doc_types import AreaDocType, UnitDocType

ALIAS_MAPPINGS = {
    'officer': (OfficerInfoDocType, Officer),
    'area': (AreaDocType, Area),
    'unit': (UnitDocType, PoliceUnit)
}
