import inspect
import sys

from cms.cms_fields import (
    PlainTextField, RandomizerField, DateField, LinkField, MultilineTextField, BaseField
)
from cms.models import CMSPage
# from story.models import Report
# from faq.models import FAQ


class BaseCMSPageDescriptor(object):
    def __init__(self, cms_page=None):
        self._fields = []

        if cms_page is not None:
            self.cms_page = cms_page
        else:
            try:
                self.cms_page = CMSPage.objects.get(descriptor_class=self.__class__.__name__)
            except CMSPage.DoesNotExist:
                self.cms_page = None

        for attr_name in dir(self):
            attribute = getattr(self, attr_name)
            if isinstance(attribute, BaseField):
                attribute.initialize(attr_name, self)
                self._fields.append(attribute)

    def get_fields(self):
        return self._fields

    def get_field_value_from_model(self, name, suffix=''):
        return self.cms_page.fields['_'.join(filter(None, [name, suffix]))]

    def seed_data(self):
        if self.cms_page:
            return

        fields_data = dict()
        for field in self._fields:
            if not field.virtual:
                data = field.seed_data()
                for key, val in data.iteritems():
                    fields_data['%s_%s' % (field.name, key)] = val

        self.cms_page = CMSPage.objects.create(
            slug=self.slug, fields=fields_data, descriptor_class=self.__class__.__name__)

    def update(self, validated_data):
        fields_data = {
            field['name']: field for field in validated_data['fields']
        }
        fields = {
            field.name: field.to_internal_value(fields_data[field.name]['value'])
            for field in self._fields if field.name in fields_data.keys()
        }
        for field_name, data in fields.iteritems():
            for key, val in data.iteritems():
                self.cms_page.fields['%s_%s' % (field_name, key)] = val
        self.cms_page.save()


class LandingPageDescriptor(BaseCMSPageDescriptor):
    slug = 'landing-page'
    reporting_header = PlainTextField(seed_value='Recent Reports')
    reporting_randomizer = RandomizerField()
    # reports = RandomizedListField(count=3, randomizer_field='reporting_randomizer', model=Report)
    faq_header = PlainTextField(seed_value='FAQ')
    faq_randomizer = RandomizerField()
    # faqs = RandomizedListField(count=3, randomizer_field='faq_randomizer', model=FAQ)
    vftg_date = DateField()
    vftg_link = LinkField()
    vftg_content = PlainTextField(seed_value='Real Independence for Police Oversight Agencies')
    collaborate_header = PlainTextField(seed_value='Collaborate')
    collaborate_content = MultilineTextField(seed_value=[
        'We are collecting and publishing information that sheds light on police misconduct.',
        'If you have documents or datasets you would like to publish, please email us, or learn more.'])
    about_header = PlainTextField(seed_value='About')
    about_content = MultilineTextField(seed_value=[
        'The Citizens Police Data Project houses police disciplinary information obtained from the City of Chicago.',
        ('The information and stories we have collected here are intended as a resource for public oversight.'
            ' Our aim is to create a new model of accountability between officers and citizens.')])


def get_descriptor(cms_page):
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if cms_page.descriptor_class == name:
            return obj(cms_page)


def get_all_descriptors():
    results = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if issubclass(obj, BaseCMSPageDescriptor):
            descriptor = obj()
            results.append(descriptor)
    return results
