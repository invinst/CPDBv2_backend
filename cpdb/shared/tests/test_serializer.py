from datetime import date

from django.test import TestCase
from rest_framework import serializers

from robber import expect
from mock import patch

from data.factories import OfficerFactory, AttachmentFileFactory, TagFactory
from data.models import AttachmentFile, Tag
from shared.serializer import (
    NoNullSerializer,
    LightweightOfficerPercentileSerializer,
    OfficerPercentileSerializer,
    CreatableSlugRelatedField,
)
from shared.tests.utils import create_object


class NoNullSerializerTestCase(TestCase):
    def test_serialization_remove_None_attr(self):

        class ObjectSerializer(NoNullSerializer):
            id = serializers.IntegerField()
            name = serializers.CharField()
        objects = [
            create_object({'id': 1, 'name': 'Alex', 'value': 3}),
            create_object({'id': 2, 'name': None, 'value': 4})
        ]

        data = ObjectSerializer(objects, many=True).data
        expect(data).to.eq([
            {'id': 1, 'name': 'Alex'},
            {'id': 2}
        ])


class LightweightOfficerPercentileSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(
            id=123,
            trr_percentile='11.11',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44',
        )
        expect(LightweightOfficerPercentileSerializer(officer).data).to.eq({
            'percentile_trr': '11.1100',
            'percentile_allegation_civilian': '33.3300',
            'percentile_allegation_internal': '44.4400',
        })


@patch('shared.serializer.MAX_VISUAL_TOKEN_YEAR', 2016)
class OfficerPercentileSerializerTestCase(TestCase):
    def test_get_data(self):
        officer = OfficerFactory(
            id=123,
            trr_percentile='11.11',
            complaint_percentile='22.22',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44',
            resignation_date=date(2013, 12, 27)
        )

        expect(OfficerPercentileSerializer(officer).data).to.eq({
            'year': 2013,
            'percentile_trr': '11.1100',
            'percentile_allegation': '22.2200',
            'percentile_allegation_civilian': '33.3300',
            'percentile_allegation_internal': '44.4400',
        })

    def test_get_data_max_year(self):
        officer = OfficerFactory(
            id=123,
            trr_percentile='11.11',
            complaint_percentile='22.22',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44',
            resignation_date=date(2017, 12, 27)
        )

        expect(OfficerPercentileSerializer(officer).data).to.eq({
            'year': 2016,
            'percentile_trr': '11.1100',
            'percentile_allegation': '22.2200',
            'percentile_allegation_civilian': '33.3300',
            'percentile_allegation_internal': '44.4400',
        })

    def test_get_data_no_resignation_date(self):
        officer = OfficerFactory(
            id=123,
            trr_percentile='11.11',
            complaint_percentile='22.22',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44',
        )

        expect(OfficerPercentileSerializer(officer).data).to.eq({
            'year': 2016,
            'percentile_trr': '11.1100',
            'percentile_allegation': '22.2200',
            'percentile_allegation_civilian': '33.3300',
            'percentile_allegation_internal': '44.4400',
        })

    def test_get_data_no_percentiles(self):
        officer = OfficerFactory(
            id=123,
            trr_percentile=None,
            complaint_percentile=None,
            civilian_allegation_percentile=None,
            internal_allegation_percentile=None,
        )

        expect(OfficerPercentileSerializer(officer).data).to.eq({
            'year': 2016
        })


class DummyAttachmentFileSerializer(serializers.ModelSerializer):
    tags = CreatableSlugRelatedField(
        slug_field='name',
        field_name='tags',
        many=True,
        queryset=Tag.objects.all(),
        max_length=20,
        required=False,
    )

    class Meta:
        model = AttachmentFile
        fields = ['tags']


class CreatableSlugRelatedFieldTestCase(TestCase):
    def test_update_with_existing_tags(self):
        tag_1 = TagFactory(name='Tag 1')
        tag_2 = TagFactory(name='Tag 2')
        tag_3 = TagFactory(name='Tag 3')

        attachment = AttachmentFileFactory(tags=[tag_1, tag_2])

        serializer = DummyAttachmentFileSerializer(instance=attachment, data={'tags': ['Tag 2', 'Tag 3']})
        serializer.is_valid()
        serializer.save()

        expect(list(attachment.tags.all())).to.eq([tag_2, tag_3])

    def test_update_with_non_existing_tags(self):
        tag_1 = TagFactory(name='Tag 1')

        attachment = AttachmentFileFactory(tags=[tag_1])

        serializer = DummyAttachmentFileSerializer(instance=attachment, data={'tags': ['Tag 2', 'Tag 3']})
        serializer.is_valid()
        serializer.save()

        tag_2 = Tag.objects.get(name='Tag 2')
        tag_3 = Tag.objects.get(name='Tag 3')

        expect(list(attachment.tags.all())).to.eq([tag_2, tag_3])

    def test_update_with_data_longer_than_max_length(self):
        tag_1 = TagFactory(name='Tag 1')

        attachment = AttachmentFileFactory(tags=[tag_1])

        serializer = DummyAttachmentFileSerializer(
            instance=attachment,
            data={'tags': ['This is a really long long long long tag']}
        )

        expect(serializer.is_valid()).to.be.false()
        message = str(serializer.errors['tags'][''][0])
        expect(message).to.eq('Ensure this field has no more than 20 characters.')
