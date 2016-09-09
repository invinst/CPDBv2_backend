import json
from datetime import date

from django.contrib.contenttypes.models import ContentType

from wagtail.wagtailimages.tests.utils import get_test_image_file
from factory.django import DjangoModelFactory
from factory import LazyFunction
from faker import Faker

from story.models import StoryPage, CoveragePage

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


class StoryFactory(DjangoModelFactory):
    class Meta:
        model = 'story.Story'  # Equivalent to ``model = myapp.models.User``

    newspaper = LazyFunction(lambda: NewspaperFactory())
    title = LazyFunction(fake.sentence)
    canonical_url = LazyFunction(fake.url)
    post_date = LazyFunction(date.today)
    body = json.dumps([{
        'type': 'paragraph',
        'value': fake.text()
        }])


class CoveragePageFactory(DjangoModelFactory):
    class Meta:
        model = 'story.CoveragePage'

    content_type = ContentType.objects.get_for_model(CoveragePage)
    title = 'Coverage'
    slug = 'coverage'


class StoryPageFactory(DjangoModelFactory):
    class Meta:
        model = 'story.StoryPage'  # Equivalent to ``model = myapp.models.User``

    content_type = ContentType.objects.get_for_model(StoryPage)
    publication_name = LazyFunction(fake.sentence)
    publication_short_url = LazyFunction(fake.url)
    author_name = LazyFunction(fake.name)
    title = LazyFunction(fake.sentence)
    canonical_url = LazyFunction(fake.url)
    post_date = LazyFunction(date.today)
    publication_date = LazyFunction(date.today)
    featured = False
    body = json.dumps([{
        'type': 'paragraph',
        'value': fake.text()
        }])
