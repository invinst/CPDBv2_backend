from django.contrib.contenttypes.models import ContentType

from data.constants import MEDIA_TYPE_DOCUMENT, MEDIA_IPRA_COPA_HIDING_TAGS
from data.models import AttachmentFile, Allegation
from analytics import constants


class LatestDocumentsQuery(object):
    @classmethod
    def execute(cls, limit):
        allegation_type_id = ContentType.objects.get(app_label='data', model='allegation').id
        data_query = f"""
            SELECT A.*,
                   ROW_NUMBER() OVER (
                      PARTITION BY A.owner_id
                      ORDER BY
                      MAX(B.created_at) DESC NULLS LAST,
                      A.external_created_at DESC NULLS LAST
                   ) AS row_number,
                   GREATEST(MAX(B.created_at), LEAST(A.external_created_at, A.created_at)) as last_active_at
            FROM data_attachmentfile AS A LEFT OUTER JOIN analytics_attachmenttracking AS B
            ON A.id = B.attachment_file_id
            AND B.kind = '{constants.VIEW_EVENT_TYPE}'
            WHERE A.file_type = '{MEDIA_TYPE_DOCUMENT}'
            AND A.owner_type_id = '{allegation_type_id}'
            AND A.show = True
            AND NOT A.tag IN ({','.join([f"'{tag}'" for tag in MEDIA_IPRA_COPA_HIDING_TAGS])})
            GROUP BY A.id
        """
        allegations_attachment_files = AttachmentFile.objects.raw(
            f"""
                SELECT * FROM ({data_query}) AS A
                WHERE A.row_number = 1 AND A.owner_type_id = '{allegation_type_id}'
                ORDER BY A.last_active_at DESC NULLS LAST
                LIMIT {limit}
            """
        )

        allegations_dict = Allegation.objects.filter(
            crid__in=[attachment.owner_id for attachment in allegations_attachment_files]
        ).select_related('most_common_category').in_bulk()

        for attachment_file in allegations_attachment_files:
            allegation_id = attachment_file.owner_id
            setattr(attachment_file, 'allegation_obj', allegations_dict[allegation_id])
            setattr(attachment_file, 'allegation_id', allegation_id)

        return allegations_attachment_files
