import inspect
import sys

from rest_framework import serializers

from cms.fields import (
    PlainTextField, RandomizerField, DateField, LinkField, MultilineTextField,
    StringField, RichTextField
)
from cms.models import ReportPage, SlugPage, FAQPage
from cms.randomizers import randomize


class BaseCMSPageSerializer(serializers.Serializer):
    def to_representation(self, obj):
        fields = []
        for field in self.fields.values():
            try:
                fields.append(field.to_representation(obj.fields))
            except KeyError:
                pass
        return {'fields': fields}

    def fake_data(self, **kwargs):
        return {
            'fields': [
                field.fake_data(kwargs.get(field_name, None))
                for field_name, field in self.fields.items()
                if not field.read_only
            ]
        }

    def to_internal_value(self, data):
        result = dict()
        for field_name, field in self.fields.iteritems():
            try:
                field_data = [
                    obj['value'] for obj in data['fields']
                    if obj['name'] == field_name][0]
            except IndexError:
                continue
            result.update(field.to_internal_value(field_data))
        return {
            'fields': result
        }

    def update(self, instance, validated_data):
        fields = validated_data.pop('fields', dict())
        instance.fields.update(fields)
        for key, val in validated_data.iteritems():
            setattr(instance, key, val)
        instance.save()
        return instance

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        return instance


class SlugPageSerializer(BaseCMSPageSerializer):
    def to_internal_value(self, data):
        validated_data = super(SlugPageSerializer, self).to_internal_value(data)
        validated_data['slug'] = self.Meta.slug
        validated_data['serializer_class'] = self.__class__.__name__
        return validated_data


class IdPageSerializer(BaseCMSPageSerializer):
    def to_representation(self, obj):
        representation = super(IdPageSerializer, self).to_representation(obj)
        representation['id'] = obj.id
        return representation


class ReportPageSerializer(IdPageSerializer):
    title = PlainTextField()
    excerpt = MultilineTextField()
    publication = StringField()
    publish_date = DateField()
    author = StringField()
    article_link = RichTextField()

    class Meta:
        model = ReportPage


class FAQPageSerializer(IdPageSerializer):
    question = PlainTextField()
    answer = MultilineTextField()

    class Meta:
        model = FAQPage


class CreateFAQPageSerializer(IdPageSerializer):
    question = PlainTextField()
    answer = MultilineTextField()

    class Meta:
        model = FAQPage

    def validate(self, data):
        if 'answer_value' in data['fields'] and not self.context['request'].user.is_authenticated():
            raise serializers.ValidationError("Unauthorized user cannot add answer.")
        return data


class LandingPageSerializer(SlugPageSerializer):
    reporting_header = PlainTextField(fake_value='Recent Reports')
    reporting_randomizer = RandomizerField()
    reports = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()
    faq_header = PlainTextField(fake_value='FAQ')
    faq_randomizer = RandomizerField()
    vftg_date = DateField()
    vftg_link = LinkField()
    vftg_content = PlainTextField(fake_value='Real Independence for Police Oversight Agencies')
    collaborate_header = PlainTextField(fake_value='Collaborate')
    collaborate_content = MultilineTextField(fake_value=[
        'We are collecting and publishing information that sheds light on police misconduct.',
        'If you have documents or datasets you would like to publish, please email us, or learn more.'])
    about_header = PlainTextField(fake_value='About')
    about_content = MultilineTextField(fake_value=[
        'The Citizens Police Data Project houses police disciplinary information obtained from the City of Chicago.',
        'The information and stories we have collected here are intended as a resource for public oversight.'
        ' Our aim is to create a new model of accountability between officers and citizens.'])

    class Meta:
        slug = 'landing-page'
        model = SlugPage

    def get_reports(self, obj):
        randomizer = self.fields['reporting_randomizer']
        randomizer_value = randomizer.to_representation(obj)['value']
        reports = randomize(
            ReportPage.objects,
            randomizer_value['poolSize'],
            3,
            randomizer_value['selectedStrategyId'])

        return {
            'name': 'reports',
            'type': 'randomized_list',
            'value': ReportPageSerializer(reports, many=True).data
        }

    def get_faqs(self, obj):
        randomizer = self.fields['faq_randomizer']
        randomizer_value = randomizer.to_representation(obj)['value']
        faqs = randomize(
            FAQPage.objects.filter(fields__has_key='answer_value'),
            randomizer_value['poolSize'],
            3,
            randomizer_value['selectedStrategyId'])

        return {
            'name': 'faqs',
            'type': 'randomized_list',
            'value': FAQPageSerializer(faqs, many=True).data
        }


def get_slug_page_serializer(cms_page):
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if cms_page.serializer_class == name:
            return obj
