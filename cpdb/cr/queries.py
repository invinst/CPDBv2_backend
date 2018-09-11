from es_index.queries import (
    DistinctQuery, AggregateQuery, GeometryQueryField, CountQueryField, ForeignQueryField,
    RowArrayQueryField
)
from data.models import (
    Allegation, Officer, OfficerAllegation, AllegationCategory, AttachmentFile, Complainant, Victim
)


class CoaccusedQuery(DistinctQuery):
    base_table = OfficerAllegation
    joins = {
        'officer': Officer,
        'ac': AllegationCategory
    }

    fields = {
        'id': 'officer.id',
        'first_name': 'officer.first_name',
        'last_name': 'officer.last_name',
        'middle_initial': 'officer.middle_initial',
        'middle_initial2': 'officer.middle_initial2',
        'suffix_name': 'officer.suffix_name',
        'gender': 'officer.gender',
        'race': 'officer.race',
        'birth_year': 'officer.birth_year',
        'rank': 'officer.rank',
        'complaint_percentile': 'officer.complaint_percentile',
        'civilian_allegation_percentile': 'officer.civilian_allegation_percentile',
        'internal_allegation_percentile': 'officer.internal_allegation_percentile',
        'trr_percentile': 'officer.trr_percentile',
        'allegation_id': 'allegation_id',
        'final_outcome': 'final_outcome',
        'final_finding': 'final_finding',
        'recc_outcome': 'recc_outcome',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'disciplined': 'disciplined',
        'allegation_count': CountQueryField(
            from_table=OfficerAllegation, related_to='officer'),
        'sustained_count': CountQueryField(
            from_table=OfficerAllegation, related_to='officer', where={'final_finding': 'SU'}),
        'allegation_name': 'ac.allegation_name',
        'category': 'ac.category',
        'category_id': 'ac.id',
    }


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
