from es_index.queries import (
    DistinctQuery, AggregateQuery, GeometryQueryField, CountQueryField, ForeignQueryField,
    Subquery, RowArrayQueryField
)
from data.models import (
    Investigator, Allegation, Officer, OfficerAllegation, InvestigatorAllegation,
    AllegationCategory, AttachmentFile, Complainant, Victim
)


class InvestigatorQuery(DistinctQuery):
    base_table = Investigator

    joins = {
        'officer': Officer
    }

    fields = {
        'id': 'id',
        'officer_id': 'officer_id',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'officer_first_name': 'officer.first_name',
        'officer_last_name': 'officer.last_name',
        'officer_middle_initial': 'officer.middle_initial',
        'officer_middle_initial2': 'officer.middle_initial2',
        'officer_suffix_name': 'officer.suffix_name',
        'complaint_percentile': 'officer.complaint_percentile',
        'civilian_allegation_percentile': 'officer.civilian_allegation_percentile',
        'internal_allegation_percentile': 'officer.internal_allegation_percentile',
        'trr_percentile': 'officer.trr_percentile',
        'num_cases': CountQueryField(from_table=InvestigatorAllegation, related_to='base_table')
    }


class InvestigatorAllegationQuery(DistinctQuery):
    base_table = InvestigatorAllegation

    joins = {
        'investigator': Subquery(InvestigatorQuery(), on='id', left_on='investigator_id')
    }

    fields = {
        'officer_id': 'investigator.officer_id',
        'allegation_id': 'allegation_id',
        'current_rank': 'current_rank',
        'investigator_first_name': 'investigator.first_name',
        'investigator_last_name': 'investigator.last_name',
        'officer_first_name': 'investigator.officer_first_name',
        'officer_last_name': 'investigator.officer_last_name',
        'officer_middle_initial': 'investigator.officer_middle_initial',
        'officer_middle_initial2': 'investigator.officer_middle_initial2',
        'officer_suffix_name': 'investigator.officer_suffix_name',
        'complaint_percentile': 'investigator.complaint_percentile',
        'civilian_allegation_percentile': 'investigator.civilian_allegation_percentile',
        'internal_allegation_percentile': 'investigator.internal_allegation_percentile',
        'trr_percentile': 'investigator.trr_percentile',
        'num_cases': 'investigator.num_cases'
    }


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
