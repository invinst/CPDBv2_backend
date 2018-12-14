import factory
import random

from faker import Faker

from email_service.models import EmailTemplate
from email_service.constants import ATTACHMENT_TYPE_CHOICES

fake = Faker()


class EmailTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailTemplate

    type = factory.LazyFunction(lambda: random.choice(ATTACHMENT_TYPE_CHOICES)[0])
    from_email = factory.LazyFunction(lambda: fake.email())
    subject = factory.LazyFunction(lambda: fake.text(32))
    body = factory.LazyFunction(lambda: fake.text(64))
