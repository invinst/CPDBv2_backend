from rest_framework import serializers

from .models import SearchTermCategory, SearchTermItem
from .term_builders import get_term_builders


class SearchTermItemSerializer(serializers.ModelSerializer):
    id = serializers.SlugField(source='slug')

    class Meta:
        model = SearchTermItem
        fields = ('id', 'name', 'description', 'call_to_action_type', 'link')


class SearchTermCategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    items = SearchTermItemSerializer(source='searchtermitem_set', many=True)

    class Meta:
        model = SearchTermCategory
        fields = ('name', 'items')
        depth = 1


class SearchTermItemWithTermsSerializer(serializers.ModelSerializer):
    id = serializers.SlugField(source='slug')
    terms = serializers.SerializerMethodField()

    class Meta:
        model = SearchTermItem
        fields = ('id', 'name', 'terms')

    def get_terms(self, obj):
        return get_term_builders(obj.slug).build_terms()
