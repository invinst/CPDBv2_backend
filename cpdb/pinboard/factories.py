import factory
from faker import Faker

from .models import Pinboard

fake = Faker()


class PinboardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pinboard

    title = factory.LazyFunction(lambda: fake.sentence())
    description = factory.LazyFunction(lambda: fake.text())

    @factory.post_generation
    def allegations(self, create, extracted, **kwargs):
        if create and extracted:
            for allegation in extracted:
                self.allegations.add(allegation)
