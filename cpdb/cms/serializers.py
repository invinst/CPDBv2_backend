import inspect
import sys

from rest_framework import serializers
from rest_framework.fields import SkipField

from cms.fields import (
    RandomizerField, DateField, LinkField,
    StringField, RichTextField, BaseCMSField
)
from cms.models import ReportPage, SlugPage, FAQPage
from cms.randomizers import randomize


class BaseCMSPageSerializer(serializers.Serializer):
    def to_representation(self, obj, use_fake=False):
        fields = []
        for field in self._presentable_fields:
            if field.write_only:
                continue
            attribute = field.get_attribute(obj)
            value = field.to_representation(attribute)
            if value is not None:
                fields.append(value)
            elif use_fake:
                fields.append(field.fake_data())

        meta_fields = dict()
        for field in self._meta_fields:
            if field.write_only:
                continue
            attribute = field.get_attribute(obj)
            value = field.to_representation(attribute)
            if value is not None:
                meta_fields[field.field_name] = value
            elif use_fake:
                meta_fields[field.field_name] = field.fake_data()

        return {'fields': fields, 'meta': meta_fields}

    @property
    def _presentable_fields(self):
        return [
            field for field in self.fields.values()
            if not hasattr(self.Meta, 'fields') or field.field_name in self.Meta.fields]

    @property
    def _meta_fields(self):
        return [
            field for field in self.fields.values()
            if field.field_name in getattr(self.Meta, 'meta_fields', [])]

    def fake_data(self, **kwargs):
        fields = []
        for field in self._presentable_fields:
            if field.read_only:
                continue
            if hasattr(field, 'fake_data'):
                fields.append(field.fake_data(kwargs.get(field.field_name, None)))
            elif field.field_name in kwargs:
                fields.append(kwargs[field.field_name])

        meta = {}
        for field in self._meta_fields:
            if field.read_only:
                continue
            if hasattr(field, 'fake_data'):
                meta[field.field_name] = field.fake_data(kwargs.get(field.field_name, None))
            elif field.field_name in kwargs:
                meta[field.field_name] = kwargs[field.field_name]

        return {'fields': fields, 'meta': meta}

    def to_internal_value(self, data):
        result = dict()
        field_values = []
        for field in self._presentable_fields:
            if 'fields' not in data:
                break
            if field.read_only:
                continue
            try:
                field_data = [
                    obj['value'] for obj in data['fields']
                    if obj['name'] == field.field_name][0]
                internal_value = field.to_internal_value(field_data)
            except (IndexError, NotImplementedError):
                continue
            field_values.append((field, internal_value))

        for field in self._meta_fields:
            if 'meta' not in data:
                break
            if field.read_only:
                continue
            try:
                internal_value = field.to_internal_value(data['meta'][field.field_name])
            except (KeyError, NotImplementedError):
                continue
            field_values.append((field, internal_value))

        supplied_fields = [field for field, _ in field_values]
        for field in self._writable_fields:
            if field in supplied_fields:
                continue
            try:
                field_values.append((field, field.get_default()))
            except SkipField:
                continue

        for field, value in field_values:
            if isinstance(field, BaseCMSField):
                result.setdefault(field.source, dict()).update(value)
            else:
                result[field.source] = value

        if 'id' in data:
            result['id'] = data['id']

        return result

    def update(self, instance, validated_data):
        validated_data.pop('id', None)
        for key, val in validated_data.iteritems():
            if isinstance(val, dict):
                getattr(instance, key).update(val)
            else:
                setattr(instance, key, val)
        instance.save()
        return instance

    def create(self, validated_data):
        validated_data.pop('id', None)
        instance = self.Meta.model.objects.create(**validated_data)
        return instance


class SlugPageSerializer(BaseCMSPageSerializer):
    def to_internal_value(self, data):
        validated_data = super(SlugPageSerializer, self).to_internal_value(data)
        validated_data['slug'] = self.Meta.slug
        validated_data['serializer_class'] = self.__class__.__name__
        return validated_data


class IdPageSerializer(BaseCMSPageSerializer):
    def to_representation(self, obj, *args, **kwargs):
        representation = super(IdPageSerializer, self).to_representation(obj, *args, **kwargs)
        representation['id'] = obj.id
        return representation


class ReportPageSerializer(IdPageSerializer):
    title = RichTextField(source='fields')
    excerpt = RichTextField(source='fields')
    publication = StringField(source='fields')
    publish_date = DateField(source='fields')
    author = StringField(source='fields')
    article_link = RichTextField(source='fields')

    class Meta:
        model = ReportPage


class FAQPageListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        data_mapping = {item['id']: item for item in validated_data}
        result = []
        for faq in instance:
            if faq.id in data_mapping:
                result.append(self.child.update(faq, data_mapping[faq.id]))

        return result


class FAQPageSerializer(IdPageSerializer):
    question = RichTextField(source='fields')
    answer = RichTextField(source='fields')
    order = serializers.IntegerField()

    class Meta:
        model = FAQPage
        fields = ('question', 'answer')
        meta_fields = ('order',)
        list_serializer_class = FAQPageListSerializer


class CreateFAQPageSerializer(IdPageSerializer):
    question = RichTextField(source='fields')
    answer = RichTextField(source='fields')
    order = serializers.IntegerField(default=lambda: FAQPage.objects.count())

    class Meta:
        model = FAQPage
        fields = ('question', 'answer')
        meta_fields = ('order',)

    def validate(self, data):
        if 'answer_value' in data['fields'] and not self.context['request'].user.is_authenticated():
            raise serializers.ValidationError("Unauthorized user cannot add answer.")
        return data


class LandingPageSerializer(SlugPageSerializer):
    reporting_header = RichTextField(fake_value=['Recent Reports'], source='fields')
    reporting_randomizer = RandomizerField(source='fields')
    reports = serializers.SerializerMethodField(source='fields')
    faqs = serializers.SerializerMethodField(source='fields')
    faq_header = RichTextField(fake_value=['FAQ'], source='fields')
    faq_randomizer = RandomizerField(source='fields')
    hero_title = RichTextField(fake_value=[
        'The Citizens Police Data Project collects and publishes information about police accountability in Chicago.'],
        source='fields')
    hero_complaint_text = RichTextField(fake_value=['Explore Complaints against police officers'], source='fields')
    hero_use_of_force_text = RichTextField(
        fake_value=['View Use of Force incidents by police officers'],
        source='fields')
    vftg_header = RichTextField(fake_value=['CPDP WEEKLY'], source='fields')
    vftg_date = DateField(source='fields')
    vftg_link = LinkField(source='fields')
    vftg_content = RichTextField(fake_value=['Real Independence for Police Oversight Agencies'], source='fields')
    collaborate_header = RichTextField(fake_value=['Collaborate'], source='fields')
    collaborate_content = RichTextField(
        fake_value=[
            'We are collecting and publishing information that sheds light on police misconduct.',
            'If you have documents or datasets you would like to publish, please email us, or learn more.'],
        source='fields')
    about_header = RichTextField(fake_value=['About'], source='fields')
    about_content = RichTextField(
        fake_value=[
            'The Citizens Police Data Project houses police disciplinary information '
            'obtained from the City of Chicago.',
            'The information and stories we have collected here are intended as a resource for public oversight.'
            ' Our aim is to create a new model of accountability between officers and citizens.'],
        source='fields')

    class Meta:
        slug = 'landing-page'
        model = SlugPage

    def get_reports(self, obj):
        randomizer = self.fields['reporting_randomizer']
        attribute = randomizer.get_attribute(obj)
        randomizer_value = randomizer.to_representation(attribute)['value']
        reports = randomize(
            ReportPage.objects,
            randomizer_value['poolSize'],
            8,
            randomizer_value['selectedStrategyId'])

        return {
            'name': 'reports',
            'type': 'randomized_list',
            'value': ReportPageSerializer(reports, many=True).data
        }

    def get_faqs(self, obj):
        randomizer = self.fields['faq_randomizer']
        attribute = randomizer.get_attribute(obj)
        randomizer_value = randomizer.to_representation(attribute)['value']
        faqs = randomize(
            FAQPage.objects.filter(fields__has_key='answer_value'),
            randomizer_value['poolSize'],
            5,
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
