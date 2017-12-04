import factory

from .models import SearchTermCategory, SearchTermItem


class SearchTermCategoryFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('word')

    class Meta:
        model = SearchTermCategory


class SearchTermItemFactory(factory.django.DjangoModelFactory):
    category = factory.SubFactory(SearchTermCategoryFactory)
    slug = factory.Faker('slug')
    name = factory.Faker('word')
    description = factory.Faker('text')

    class Meta:
        model = SearchTermItem
