from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from factory.django import DjangoModelFactory
from factory import LazyFunction, LazyAttribute
from faker import Faker

User = get_user_model()
fake = Faker()


class AdminUserFactory(DjangoModelFactory):
    class Meta:
        model = User

    class Params:
        raw_password = LazyFunction(fake.password)

    username = LazyFunction(fake.user_name)
    password = LazyAttribute(lambda a: make_password(a.raw_password))
    is_staff = True
    is_active = True
