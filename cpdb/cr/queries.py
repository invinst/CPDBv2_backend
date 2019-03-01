from django.db import connection

from data.constants import MEDIA_TYPE_DOCUMENT, MEDIA_IPRA_COPA_HIDING_TAGS
from data.models import AttachmentFile
from analytics import constants
from utils.raw_query_utils import dict_fetch_all


class LatestDocumentsQuery(object):
    @staticmethod
    def _num_recent_documents_hash(attachment_files):
        data_query = f"""
            SELECT data_attachmentfile.id,
                   data_attachmentfile.allegation_id,
                   data_attachmentfile.external_created_at,
                   MAX(data_attachmentfile.external_created_at) OVER (PARTITION BY data_attachmentfile.allegation_id)
                   AS latest_created_at
            FROM data_attachmentfile
            WHERE data_attachmentfile.file_type = '{MEDIA_TYPE_DOCUMENT}'
            AND data_attachmentfile.show = True
            AND NOT data_attachmentfile.tag IN ({','.join([f"'{tag}'" for tag in MEDIA_IPRA_COPA_HIDING_TAGS])})
            GROUP BY data_attachmentfile.id
        """

        num_recent_documents_query = f"""
            SELECT A.allegation_id, count(A.id) FROM ({data_query}) AS A
            WHERE A.external_created_at >= A.latest_created_at  - INTERVAL '30 days'
            AND A.allegation_id
            IN ({','.join([f"'{str(attachment_file.allegation_id)}'" for attachment_file in attachment_files])})
            GROUP BY A.allegation_id
        """

        with connection.cursor() as cursor:
            cursor.execute(num_recent_documents_query)
            num_recent_documents_result = dict_fetch_all(cursor)
        return {row['allegation_id']: row['count'] for row in num_recent_documents_result}

    @classmethod
    def execute(cls, limit):
        data_query = f"""
            SELECT data_attachmentfile.*,
                   MAX(B.created_at) AS latest_viewed_at,
                   ROW_NUMBER() OVER (
                      PARTITION BY data_attachmentfile.allegation_id
                      ORDER BY
                      MAX(B.created_at) DESC NULLS LAST,
                      data_attachmentfile.external_created_at DESC NULLS LAST
                   ) AS row_number
            FROM data_attachmentfile LEFT OUTER JOIN (
                SELECT * FROM analytics_attachmenttracking
                WHERE analytics_attachmenttracking.kind = '{constants.VIEW_EVENT_TYPE}'
            ) AS B
            ON data_attachmentfile.id = B.attachment_file_id
            WHERE data_attachmentfile.file_type = '{MEDIA_TYPE_DOCUMENT}'
            AND data_attachmentfile.show = True
            AND NOT data_attachmentfile.tag IN ({','.join([f"'{tag}'" for tag in MEDIA_IPRA_COPA_HIDING_TAGS])})
            GROUP BY data_attachmentfile.id
        """
        attachment_files = AttachmentFile.objects.raw(
            f"""
                SELECT * FROM ({data_query}) AS A
                WHERE A.row_number = 1
                ORDER BY A.latest_viewed_at DESC NULLS LAST, A.external_created_at DESC NULLS LAST
                LIMIT {limit}
            """
        )

        num_recent_documents_hash = cls._num_recent_documents_hash(attachment_files)

        for attachment_file in attachment_files:
            setattr(attachment_file, 'num_recent_documents', num_recent_documents_hash[attachment_file.allegation_id])

        return attachment_files
