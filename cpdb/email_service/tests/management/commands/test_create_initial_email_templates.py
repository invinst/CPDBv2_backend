from django.core import management
from django.test import TestCase
from robber import expect

from email_service.models import EmailTemplate
from email_service.constants import (
    CR_ATTACHMENT_REQUEST, CR_ATTACHMENT_AVAILABLE, TRR_ATTACHMENT_REQUEST, TRR_ATTACHMENT_AVAILABLE
)


class CreateInitialEmailTemplatesCommandTestCase(TestCase):
    def test_create_initial_email_templates(self):
        expect(EmailTemplate.objects.count()).to.eq(0)

        management.call_command('create_initial_email_templates')

        templates = EmailTemplate.objects.all()
        expect(templates).to.have.length(4)
        expect({template.type for template in templates}).to.eq({
            CR_ATTACHMENT_REQUEST, CR_ATTACHMENT_AVAILABLE, TRR_ATTACHMENT_REQUEST, TRR_ATTACHMENT_AVAILABLE
        })
