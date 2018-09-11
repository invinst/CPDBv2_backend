from es_index.queries import (
    AggregateQuery, RowArrayQueryField, DistinctQuery, CountQueryField,
    ForeignQueryField, GeometryQueryField
)
from data.models import (
    Officer, OfficerAllegation, OfficerHistory,
    Allegation, Victim, AttachmentFile, PoliceUnit
)
from trr.models import TRR


class OfficerHistoryQuery(DistinctQuery):
    base_table = OfficerHistory

    joins = {
        'unit': PoliceUnit
    }

    fields = {
        'officer_id': 'officer_id',
        'unit_id': 'unit_id',
        'unit_name': 'unit.unit_name',
        'description': 'unit.description',
        'end_date': 'end_date',
        'effective_date': 'effective_date'
    }


class OfficerQuery(AggregateQuery):
    base_table = Officer

    fields = {
        'id': 'id',
        'date_of_appt': 'appointed_date',
        'date_of_resignation': 'resignation_date',
        'active': 'active',
        'rank': 'rank',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'middle_initial': 'middle_initial',
        'middle_initial2': 'middle_initial2',
        'suffix_name': 'suffix_name',
        'race': 'race',
        'gender': 'gender',
        'birth_year': 'birth_year',
        'allegation_count': CountQueryField(
            from_table=OfficerAllegation, related_to='base_table'),
        'sustained_count': CountQueryField(
            from_table=OfficerAllegation, related_to='base_table', where={'final_finding': 'SU'}),
        'complaint_percentile': 'complaint_percentile',
        'honorable_mention_percentile': 'honorable_mention_percentile',
        'discipline_count': CountQueryField(
            from_table=OfficerAllegation, related_to='base_table', where={'disciplined': True}),
        'civilian_allegation_percentile': 'civilian_allegation_percentile',
        'internal_allegation_percentile': 'internal_allegation_percentile',
        'trr_percentile': 'trr_percentile',
        'trr_count': CountQueryField(
            from_table=TRR, related_to='base_table'),
        'tags': 'tags',
        'unsustained_count': CountQueryField(
            from_table=OfficerAllegation, related_to='base_table', where={'final_finding': 'NS'})
    }


class AllegationTimelineQuery(AggregateQuery):
    base_table = Allegation

    joins = {
        'attachments': AttachmentFile,
        'victims': Victim
    }

    fields = {
        'coaccused_count': CountQueryField(
            from_table=OfficerAllegation, related_to='base_table'
        ),
        'id': 'id',
        'point': GeometryQueryField('point'),
        'crid': 'crid',
        'attachments': RowArrayQueryField('attachments'),
        'victims': RowArrayQueryField('victims'),
    }


class CRTimelineQuery(DistinctQuery):
    base_table = OfficerAllegation

    fields = {
        'officer_id': 'officer_id',
        'allegation_id': 'allegation_id',
        'start_date': 'start_date',
        'category': ForeignQueryField(
            relation='allegation_category_id', field_name='category'),
        'subcategory': ForeignQueryField(
            relation='allegation_category_id', field_name='allegation_name'),
        'final_finding': 'final_finding',
        'final_outcome': 'final_outcome',
    }
