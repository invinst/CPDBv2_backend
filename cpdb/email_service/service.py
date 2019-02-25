import logging
import re
from smtplib import SMTPException

from django.core.mail import send_mail
from django.conf import settings

from tqdm import tqdm

from email_service.models import EmailTemplate
from email_service.constants import CR_ATTACHMENT_AVAILABLE
from data.models import Allegation, AttachmentFile

logger = logging.getLogger(__name__)


def _get_name_from_email(email):
    return re.match(r'.+?(?=@)', email).group(0)


def send_cr_attachment_available_email(new_attachments):
    email_template = EmailTemplate.objects.get(type=CR_ATTACHMENT_AVAILABLE)

    crids = {attachment.allegation.crid for attachment in new_attachments}

    for crid in tqdm(crids, desc='Sending notification emails'):
        allegation = Allegation.objects.get(crid=crid)
        for attachment_request in allegation.attachmentrequest_set.filter(noti_email_sent=False):
            message = email_template.create_message(
                [attachment_request.email],
                name=_get_name_from_email(attachment_request.email),
                pk=crid,
                url=f'{settings.DOMAIN}{allegation.v2_to}'
            )
            try:
                send_mail(**message)
            except SMTPException:
                logger.info(f'Cannot send notification email for crid {crid} to {attachment_request.email}')
            else:
                attachment_request.noti_email_sent = True
                attachment_request.save()

                for attachment in new_attachments:
                    if attachment.allegation == attachment_request.allegation:
                        attachment.notifications_count = len(message)

    AttachmentFile.objects.bulk_update(
        new_attachments,
        update_fields=['notifications_count'],
        batch_size=1000
    )


def send_attachment_request_email(email, attachment_type, **kwargs):
    email_template = EmailTemplate.objects.get(type=attachment_type)
    name = _get_name_from_email(email)
    message = email_template.create_message([email], name=name, **kwargs)
    send_mail(**message)
