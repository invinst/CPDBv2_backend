import json

from factory.django import DjangoModelFactory, ImageField
from factory import SubFactory, LazyFunction
from faker import Faker


fake = Faker()


class NewspaperFactory(DjangoModelFactory):
    class Meta:
        model = 'story.Newspaper'

    name = LazyFunction(fake.sentence)
    short_name = LazyFunction(fake.sentence)


class StoryPageFactory(DjangoModelFactory):
    class Meta:
        model = 'story.StoryPage'  # Equivalent to ``model = myapp.models.User``

    newspaper = SubFactory(NewspaperFactory)
    title = LazyFunction(fake.sentence)
    canonical_url = LazyFunction(fake.url)
    post_date = LazyFunction(fake.date_time_this_month)
    image = ImageField()
    body = json.dumps([{
        'type': 'paragraph',
        'value': fake.text()
        }])
