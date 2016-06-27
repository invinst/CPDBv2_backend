# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-03 10:37
from __future__ import unicode_literals

import os, json
from sys import path

from django.db import migrations
from django.core import serializers
from django.utils.text import slugify

fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
fixture_filename = 'initial_faqs.json'


def load_fixture(apps, schema_editor):
    ContentType = apps.get_model('contenttypes.ContentType')
    Page = apps.get_model('wagtailcore', 'page')
    FAQPage = apps.get_model('faq', 'faqpage')
    root_page = Page.objects.get(pk=2)

    fixture_file = os.path.join(fixture_dir, fixture_filename)
    try:
        fixture = open(fixture_file, 'rb')
        fixture_data = json.loads(fixture.read())
        faqpage_content_type, created = ContentType.objects.get_or_create(
            model='faqpage',
            app_label='faq'
        )

        for datum in fixture_data:
            datum_model = datum.pop('model', None)
            if datum_model == 'faq.faqpage':
                root_page.numchild += 1
                slug = slugify(datum.get('fields', {}).get('title', '{id}'.format(id=root_page.numchild)), allow_unicode=True)
                faq_page = datum.get('fields', {}).update({
                    'path': '{root_path}{index:04d}'.format(root_path=root_page.path, index=root_page.numchild),
                    'depth': root_page.depth + 1,
                    'url_path': '{root_url}{slug}/'.format(root_url=root_page.url_path, slug=slug),
                    'content_type': faqpage_content_type
                    })
                FAQPage.objects.create(**datum.get('fields', None))

        root_page.save()
    except Exception, e:
        raise e
    finally:
        fixture.close()

def unload_fixture(apps, schema_editor):
    FAQPage = apps.get_model('faq', 'faqpage')
    Page = apps.get_model('wagtailcore', 'page')
    root_page = Page.objects.get(pk=2)

    numfaq = FAQPage.objects.count()
    root_page.numchild -= numfaq

    FAQPage.objects.all().delete()
    root_page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('faq', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture)
    ]
