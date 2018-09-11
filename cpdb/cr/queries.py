from es_index.queries import (
    AggregateQuery, GeometryQueryField, ForeignQueryField,
    RowArrayQueryField
)
from data.models import (
    Allegation, AttachmentFile, Complainant, Victim
)


class AllegationQuery(AggregateQuery):
    base_table = Allegation
    joins = {
        'attachment_files': AttachmentFile,
        'complainants': Complainant,
        'victims': Victim
    }

    fields = {
        'crid': 'crid',
        'id': 'id',
        'attachments': RowArrayQueryField('attachment_files'),
        'complainants': RowArrayQueryField('complainants'),
        'victims': RowArrayQueryField('victims'),
        'beat': ForeignQueryField(relation='beat_id', field_name='name'),
        'summary': 'summary',
        'point': GeometryQueryField('point'),
        'incident_date': 'incident_date',
        'old_complaint_address': 'old_complaint_address',
        'add1': 'add1',
        'add2': 'add2',
        'city': 'city',
        'location': 'location',
    }
