import inspect
import sys

from django.db import models
from rest_framework import serializers
from rest_framework.fields import SkipField

from cms.fields import RichTextField, BaseCMSField
from cms.models import SlugPage


class BaseCMSPageSerializer(serializers.Serializer):
    def to_representation(self, obj, use_fake=False):
        def _transform_field_value(_fields):
            for field in _fields:
                if field.write_only:
                    continue
                attribute = field.get_attribute(obj)
                value = field.to_representation(attribute)
                if value is not None:
                    yield (value, field)
                elif use_fake:
                    yield (field.fake_data(), field)

        fields = []
        for value, _ in _transform_field_value(self._non_meta_fields):
            fields.append(value)

        meta_fields = dict()
        for value, field in _transform_field_value(self._meta_fields):
            meta_fields[field.field_name] = value

        return {'fields': fields, 'meta': meta_fields}

    @property
    def _non_meta_fields(self):
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
        for field in self._non_meta_fields:
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
        if 'fields' in data:
            for field in self._non_meta_fields:
                if field.read_only:
                    continue
                try:
                    field_data = [
                        obj['value'] for obj in data['fields']
                        if obj['name'] == field.field_name
                    ][0]
                    internal_value = field.to_internal_value(field_data)
                except (IndexError, NotImplementedError):
                    continue
                field_values.append((field, internal_value))
        if 'meta' in data:
            for field in self._meta_fields:
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
        for key, val in validated_data.items():
            if isinstance(val, dict):
                getattr(instance, key).update(val)
            elif isinstance(instance._meta.get_field(key), models.ManyToManyField):
                getattr(instance, key).set(val)
            else:
                setattr(instance, key, val)
        instance.save()
        return instance

    def create(self, validated_data):
        validated_data.pop('id', None)

        relation_fields = []
        for field in self.fields.values():
            if hasattr(field, 'child') and isinstance(field.child, serializers.ModelSerializer):
                value = validated_data.pop(field.source, None)
                if value is not None:
                    relation_fields.append((field.source, value))

        instance = self.Meta.model.objects.create(**validated_data)
        for key, value in relation_fields:
            attr = getattr(instance, key)
            attr.add(*value)

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


class LandingPageSerializer(SlugPageSerializer):
    navbar_title = RichTextField(
        fake_value=['Citizens Police Data Project'],
        source='fields'
    )
    navbar_subtitle = RichTextField(
        fake_value=[
            'collects and information',
            'about police misconduct in Chicago.'
        ],
        source='fields'
    )
    carousel_complaint_title = RichTextField(
        fake_value=['Complaint Summaries'],
        source='fields'
    )
    carousel_complaint_desc = RichTextField(
        fake_value=['These records contain summary information of the incident of the alleged complaint.'],
        source='fields'
    )
    carousel_allegation_title = RichTextField(
        fake_value=['Officers by Allegation'],
        source='fields'
    )
    carousel_allegation_desc = RichTextField(
        fake_value=['These are the officers with the most allegations of misconduct in Chicago.'],
        source='fields'
    )
    carousel_document_title = RichTextField(
        fake_value=['New Document'],
        source='fields'
    )
    carousel_document_desc = RichTextField(
        fake_value=['We often update our complaint records as we recieve more information from the City.',
                    'Here are some of the recent updates.'],
        source='fields'
    )
    carousel_activity_title = RichTextField(
        fake_value=['Recent Activity'],
        source='fields'
    )
    carousel_activity_desc = RichTextField(
        fake_value=['The officers, pairings, and units we display here are based on what other guests are searching '
                    'on cpdp in addition to officers who are mentioned in conversation with our twitter bot,@cpdpbot'],
        source='fields'
    )
    carousel_lawsuit_title = RichTextField(
        fake_value=['Lawsuits'],
        source='fields'
    )
    carousel_lawsuit_desc = RichTextField(
        fake_value=['In partnership with The Chicago Reporter, CPDP now contains data and documents relating to the '
                    '1,112 lawsuits that resulted in the City of Chicago paying $313 million in settlements.'],
        source='fields'
    )
    demo_video_text = RichTextField(
        fake_value=['What is CPDP?'],
        source='fields'
    )

    class Meta:
        slug = 'landing-page'
        model = SlugPage


class OfficerPageSerializer(SlugPageSerializer):
    triangle_description = RichTextField(
        fake_value=[
            'The corners of the triangle show the percentile score for this officer in each of three types of data: '
            'complaints from civilians, complaints from other officers, and self-reported uses of force.'
        ],
        source='fields'
    )
    triangle_sub_description = RichTextField(
        fake_value=[
            'If one corner of the black inner triangle is close to reaching the outer triangle, '
            'then this officer is named in a relatively high rate of incidents of that '
            'type compared with other officers.'
        ],
        source='fields'
    )
    scale_description = RichTextField(
        fake_value=[
            'If an officer\'s percentile rank for civilian complaints is 99% then this means that '
            'they were accused in more civilian complaints per year than 99% of other officers.'
        ],
        source='fields'
    )
    scale_sub_description = RichTextField(
        fake_value=[
            'Civilian and internal complaint percentiles are based on data '
            'that is only available since 2000, use of force data is only available since 2004. '
            'The overall allegation count percentiles displayed on '
            'the officer profile page are calculated using data that reaches back to 1988.'
        ],
        source='fields'
    )
    no_data_explain_text = RichTextField(
        fake_value=[
            'There is not enough data to construct',
            'a radar graph for this officer.'
        ],
        source='fields'
    )

    class Meta:
        slug = 'officer-page'
        model = SlugPage


class CRPageSerializer(SlugPageSerializer):
    document_request_instruction = RichTextField(
        fake_value=['We’ll notify you when the document is made available.'],
        source='fields'
    )

    no_attachment_text = RichTextField(
        fake_value=['There are no documents that have been made public yet.'],
        source='fields'
    )

    new_document_notification = RichTextField(
        fake_value=['We’ll notify you when we have new documents.'],
        source='fields'
    )

    class Meta:
        slug = 'cr-page'
        model = SlugPage


class TRRPageSerializer(SlugPageSerializer):
    document_request_instruction = RichTextField(
        fake_value=['We’ll notify you when the document is made available.'],
        source='fields'
    )
    no_attachment_text = RichTextField(
        fake_value=['There are no documents that have been made public yet.'],
        source='fields'
    )

    class Meta:
        slug = 'trr-page'
        model = SlugPage


class PinboardPageSerializer(SlugPageSerializer):
    empty_pinboard_title = RichTextField(
        fake_value=['Get started'],
        source='fields'
    )
    empty_pinboard_description = RichTextField(
        fake_value=[
            'Use search to find officers and individual complaint records and press the plus button to add cards to '
            'your pinboard.',
            '',
            'Come back to the pinboard to give it a title and see a network map or discover relevant documents.'
        ],
        source='fields'
    )

    class Meta:
        slug = 'pinboard-page'
        model = SlugPage


def get_slug_page_serializer(cms_page):
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if cms_page.serializer_class == name:
            return obj
