import factory
from faker import Faker

from toast.models import Toast

fake = Faker()


class ToastFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Toast

    name = factory.LazyFunction(lambda: fake.word())
    template = factory.LazyFunction(lambda: fake.text(512))
    tags = factory.LazyFunction(lambda: fake.pylist(2, False, str))
