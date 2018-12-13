from django.core.mail import send_mail
from django.conf import settings

from tqdm import tqdm

from email_service.models import EmailTemplate
from email_service.constants import ATTACHMENT_AVAILABLE, ATTACHMENT_REQUEST
from data.models import Allegation, AttachmentRequest


def send_attachment_available_notification(new_attachments):
    email_template = EmailTemplate.objects.get(type=ATTACHMENT_AVAILABLE)

    crids = {attachment.allegation.crid for attachment in new_attachments}
    for crid in tqdm(crids, desc='Sending notification emails'):
        allegation = Allegation.objects.get(crid=crid)
        for attachment_request in allegation.attachmentrequest_set.filter(noti_email_sent=False):
            send_mail(*email_template.create_message(
                [attachment_request.email],
                crid=crid,
                cr_page_url=f'{settings.DOMAIN}{allegation.v2_to}'
            ))

    AttachmentRequest.objects.filter(allegation__crid__in=crids).update(noti_email_sent=True)


def send_attachment_request_welcome_email(email, crid):
    email_template = EmailTemplate.objects.get(type=ATTACHMENT_REQUEST)

    message = email_template.create_message([email], crid=crid)
    send_mail(*message)
