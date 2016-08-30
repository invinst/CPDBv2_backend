from factory.django import DjangoModelFactory
from factory import SubFactory
from faker import Faker

from faq.factories import FAQFactory
from landing_page.models import LandingPage
from story.factories import StoryFactory

fake = Faker()


class LandingPageFactory(DjangoModelFactory):
    class Meta:
        model = LandingPage

    title = 'Landing Page'
    report1 = SubFactory(StoryFactory)
    report2 = SubFactory(StoryFactory)
    report3 = SubFactory(StoryFactory)
    faq1 = SubFactory(FAQFactory)
    faq2 = SubFactory(FAQFactory)
    faq3 = SubFactory(FAQFactory)
