import factory

from faker import Faker

from .models import AppliedFixture

fake = Faker()


class AppliedFixtureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AppliedFixture

    file_name = factory.LazyFunction(lambda: fake.name())
