from django.core.management import call_command
from django.test import TestCase

from robber import expect
from mock import patch

from cms.fields import RichTextField
from cms.models import SlugPage
from cms.serializers import SlugPageSerializer, LandingPageSerializer, get_slug_page_serializer


class TestingPageSerializer(SlugPageSerializer):
    first_field = RichTextField(
        fake_value=['This is the initial value for first_field'],
        source='fields'
    )
    second_field = RichTextField(
        fake_value=['This is the initial value for second_field'],
        source='fields'
    )

    class Meta:
        slug = 'testing-page'
        model = SlugPage


def get_slug_page_serializer_mock(cms_page):
    if cms_page.slug == 'testing-page':
        return TestingPageSerializer
    else:
        return get_slug_page_serializer(cms_page)


class UpdateFieldsCommandTestCase(TestCase):
    def setUp(self):
        testing_page_serializer = TestingPageSerializer(data=TestingPageSerializer().fake_data())
        testing_page_serializer.is_valid()
        testing_page_serializer.save()

    def test_create_new_field(self):
        testing_page = SlugPage.objects.get(slug='testing-page')
        testing_page.fields.pop('second_field_type')
        testing_page.fields.pop('second_field_value')
        testing_page.save()

        testing_page.refresh_from_db()
        expect(testing_page.fields).not_to.contain('second_field_type')
        expect(testing_page.fields).not_to.contain('second_field_value')

        with patch('cms.serializers.get_slug_page_serializer', get_slug_page_serializer_mock):
            call_command('cms_update_fields')

        testing_page.refresh_from_db()
        expect(testing_page.fields).to.contain('second_field_type')
        expect(testing_page.fields).to.contain('second_field_value')
        expect(
            [block['text'] for block in testing_page.fields['second_field_value']['blocks']]
        ).to.eq(['This is the initial value for second_field'])

    def test_delete_old_field(self):
        class OldTestingPageSerializer(SlugPageSerializer):
            first_field = RichTextField(
                fake_value=['This is the initial value for first_field'],
                source='fields'
            )
            second_field = RichTextField(
                fake_value=['This is the initial value for second_field'],
                source='fields'
            )
            third_field = RichTextField(
                fake_value=['This is the initial value for third_field'],
                source='fields'
            )

            class Meta:
                slug = 'testing-page'
                model = SlugPage

        testing_page = SlugPage.objects.get(slug='testing-page')
        old_data = OldTestingPageSerializer().to_representation(testing_page, use_fake=True)
        old_fields = OldTestingPageSerializer().to_internal_value(old_data)['fields']
        testing_page.fields = old_fields
        testing_page.save()

        testing_page.refresh_from_db()
        expect(set(testing_page.fields.keys())).to.eq({
            'first_field_type', 'first_field_value',
            'second_field_type', 'second_field_value',
            'third_field_type', 'third_field_value'
        })

        with patch('cms.serializers.get_slug_page_serializer', get_slug_page_serializer_mock):
            call_command('cms_update_fields')

        testing_page.refresh_from_db()
        expect(set(testing_page.fields.keys())).to.eq({
            'first_field_type', 'first_field_value',
            'second_field_type', 'second_field_value'
        })

    def test_update_one_page(self):
        landing_page_serializer = LandingPageSerializer(data=LandingPageSerializer().fake_data())
        landing_page_serializer.is_valid()
        landing_page_serializer.save()

        expect(SlugPage.objects.count()).to.eq(2)
        landing_page = SlugPage.objects.get(slug='landing-page')
        testing_page = SlugPage.objects.get(slug='testing-page')

        expect(testing_page.fields).to.contain('second_field_type')
        expect(testing_page.fields).to.contain('second_field_value')
        expect(landing_page.fields).to.contain('navbar_subtitle_type')
        expect(landing_page.fields).to.contain('navbar_subtitle_value')

        testing_page.fields.pop('second_field_type')
        testing_page.fields.pop('second_field_value')
        testing_page.save()
        landing_page.fields.pop('navbar_subtitle_type')
        landing_page.fields.pop('navbar_subtitle_value')
        landing_page.save()

        testing_page.refresh_from_db()
        landing_page.refresh_from_db()
        expect(testing_page.fields).not_to.contain('second_field_type')
        expect(testing_page.fields).not_to.contain('second_field_value')
        expect(landing_page.fields).not_to.contain('navbar_subtitle_type')
        expect(landing_page.fields).not_to.contain('navbar_subtitle_value')

        with patch('cms.serializers.get_slug_page_serializer', get_slug_page_serializer_mock):
            call_command('cms_update_fields', 'testing-page')

        testing_page.refresh_from_db()
        landing_page.refresh_from_db()

        expect(testing_page.fields).to.contain('second_field_type')
        expect(testing_page.fields).to.contain('second_field_value')
        expect(
            [block['text'] for block in testing_page.fields['second_field_value']['blocks']]
        ).to.eq(['This is the initial value for second_field'])

        expect(landing_page.fields).not_to.contain('navbar_subtitle_type')
        expect(landing_page.fields).not_to.contain('navbar_subtitle_value')
