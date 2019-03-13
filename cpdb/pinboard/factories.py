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
    def officers(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for officer in extracted:
                self.officers.add(officer)

    @factory.post_generation
    def allegations(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for allegation in extracted:
                self.allegations.add(allegation)
