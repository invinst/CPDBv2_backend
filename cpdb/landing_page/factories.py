from factory.django import DjangoModelFactory
from faker import Faker

from landing_page.models import LandingPage

fake = Faker()


class LandingPageFactory(DjangoModelFactory):
    class Meta:
        model = LandingPage

    title = 'Landing Page'
