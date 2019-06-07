import functools
from django.db import connection

from social_graph.serializers.officer_serializer import OfficerSerializer
from social_graph.serializers.accused_serializer import AccusedSerializer
from data.models import Officer, Allegation
from utils.raw_query_utils import dict_fetch_all


DEFAULT_THRESHOLD = 2
DEFAULT_SHOW_CIVIL_ONLY = True


class SocialGraphDataQuery(object):
    def __init__(
        self,
        officers,
        threshold=DEFAULT_THRESHOLD,
        show_civil_only=DEFAULT_SHOW_CIVIL_ONLY,
        show_connected_officers=False,
    ):
        self.officers = officers
        self.threshold = threshold if threshold else DEFAULT_THRESHOLD
        self.show_civil_only = show_civil_only if show_civil_only is not None else DEFAULT_SHOW_CIVIL_ONLY
        self.show_connected_officers = show_connected_officers

    def _build_query(self):
        officer_ids_string = ", ".join([str(officer.id) for officer in self.officers])
        coaccused_data_query = f"""
            SELECT A.officer_id AS officer_id_1,
                   B.officer_id AS officer_id_2,
                   A.allegation_id AS allegation_id,
                   data_allegation.incident_date AS incident_date,
                   ROW_NUMBER() OVER (PARTITION BY A.officer_id, B.officer_id ORDER BY incident_date) AS accussed_count
            FROM data_officerallegation AS A
            INNER JOIN data_officerallegation AS B ON A.allegation_id = B.allegation_id
            LEFT JOIN data_allegation ON data_allegation.crid = A.allegation_id
            WHERE A.officer_id < B.officer_id
            AND (
                B.officer_id IN ({officer_ids_string})
                {'OR' if self.show_connected_officers else 'AND'} A.officer_id IN ({officer_ids_string})
            )
            AND data_allegation.incident_date IS NOT NULL
            {'AND data_allegation.is_officer_complaint IS FALSE' if self.show_civil_only else ''}
        """
        return f"""
            SELECT * FROM ({coaccused_data_query}) coaccused_data WHERE accussed_count >= {self.threshold}
            ORDER BY incident_date
        """

    @property
    @functools.lru_cache()
    def coaccused_data(self):
        if self.officers:
            with connection.cursor() as cursor:
                cursor.execute(self._build_query())
                return dict_fetch_all(cursor)
        else:
            return []

    def list_event(self):
        events = list({row['incident_date'].date().strftime(format='%Y-%m-%d') for row in self.coaccused_data})
        events.sort()
        return events

    def all_officers(self):
        if self.show_connected_officers:
            officer_ids = [row['officer_id_1'] for row in self.coaccused_data]
            officer_ids += [row['officer_id_2'] for row in self.coaccused_data]
            officer_ids += [officer.id for officer in self.officers]
            officer_ids = list(set(officer_ids))
            return Officer.objects.filter(id__in=officer_ids).order_by('first_name', 'last_name')
        else:
            return self.officers.order_by('first_name', 'last_name')

    def graph_data(self):
        if self.officers:
            return {
                'coaccused_data': AccusedSerializer(self.coaccused_data, many=True).data,
                'officers': OfficerSerializer(self.all_officers(), many=True).data,
                'list_event': self.list_event()
            }
        else:
            return {}

    def allegations(self):
        allegation_ids = list({row['allegation_id'] for row in self.coaccused_data})
        return Allegation.objects.filter(crid__in=allegation_ids).order_by('incident_date')
