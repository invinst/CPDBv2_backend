from factory.django import DjangoModelFactory
from faker import Faker

from landing_page.models import LandingPage, LandingPageContent

fake = Faker()


class LandingPageFactory(DjangoModelFactory):
    class Meta:
        model = LandingPage

    title = 'Landing Page'


class LandingPageContentFactory(DjangoModelFactory):
    class Meta:
        model = LandingPageContent

    collaborate_header = 'Collaborate with us'
