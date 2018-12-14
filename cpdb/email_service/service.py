import re

from django.core.mail import send_mail
from django.conf import settings

from tqdm import tqdm

from email_service.models import EmailTemplate
from email_service.constants import CR_ATTACHMENT_AVAILABLE, CR_ATTACHMENT_REQUEST
from data.models import Allegation, AttachmentRequest


def send_cr_attachment_available_email(new_attachments):
    email_template = EmailTemplate.objects.get(type=CR_ATTACHMENT_AVAILABLE)

    crids = {attachment.allegation.crid for attachment in new_attachments}
    for crid in tqdm(crids, desc='Sending notification emails'):
        allegation = Allegation.objects.get(crid=crid)
        for attachment_request in allegation.attachmentrequest_set.filter(noti_email_sent=False):
            send_mail(*email_template.create_message(
                [attachment_request.email],
                pk=crid,
                url=f'{settings.DOMAIN}{allegation.v2_to}'
            ))

    AttachmentRequest.objects.filter(allegation__crid__in=crids).update(noti_email_sent=True)


def send_attachment_request_email(email, attachment_type, **kwargs):
    email_template = EmailTemplate.objects.get(type=attachment_type)
    name = re.match(r'.+?(?=@)', email).group(0)
    message = email_template.create_message([email], name=name, **kwargs)
    send_mail(**message)
