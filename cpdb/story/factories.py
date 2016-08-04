import json
from datetime import date

from django.contrib.contenttypes.models import ContentType

from wagtail.wagtailimages.tests.utils import get_test_image_file

from factory.django import DjangoModelFactory
from factory import SubFactory, LazyFunction
from faker import Faker

from story.models import StoryPage

fake = Faker()


class ImageFactory(DjangoModelFactory):
    class Meta:
        model = 'wagtailimages.Image'

    title = LazyFunction(fake.sentence)
    file = LazyFunction(get_test_image_file)


class NewspaperFactory(DjangoModelFactory):
    class Meta:
        model = 'story.Newspaper'

    name = LazyFunction(fake.sentence)
    short_name = LazyFunction(fake.sentence)


class StoryPageFactory(DjangoModelFactory):
    class Meta:
        model = 'story.StoryPage'  # Equivalent to ``model = myapp.models.User``

    content_type = ContentType.objects.get_for_model(StoryPage)
    newspaper = SubFactory(NewspaperFactory)
    title = LazyFunction(fake.sentence)
    canonical_url = LazyFunction(fake.url)
    post_date = LazyFunction(date.today)
    body = json.dumps([{
        'type': 'paragraph',
        'value': fake.text()
        }])
    is_featured = False
