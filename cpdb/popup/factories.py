import factory
from faker import Faker

from popup.models import Popup

fake = Faker()


class PopupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Popup

    name = factory.LazyFunction(lambda: fake.word())
    page = factory.LazyFunction(lambda: fake.word())
    title = factory.LazyFunction(lambda: fake.word())
    text = factory.LazyFunction(lambda: fake.text(512))
