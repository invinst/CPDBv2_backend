# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict
from datetime import datetime

import iso8601
import pytz

from data.constants import AttachmentSourceType, MEDIA_TYPE_DOCUMENT


class Field(object):
    pass


class Just(Field):
    def __init__(self, value):
        self.value = value

    def parse(self, _):
        return self.value


class SimpleField(Field):
    def __init__(self, field_name='', ignore_values=None):
        self.field_name = field_name
        self.ignore_values = ignore_values or []

    def parse(self, row):
        return row


class CharField(SimpleField):
    def parse(self, row):
        value = row.get(self.field_name, '')

        # We accept the fact that no-value of string is ''. Should reconsider when we work with a complete solution to
        # differentiate between no-value and empty value.
        if not value:
            return ''

        return value.strip()


class MediaTypeField(CharField):
    def parse(self, row):
        value = row.get(self.field_name, '')

        if value.lower().startswith('video'):
            return 'video'

        if value.lower().startswith('audio'):
            return 'audio'

        return 'document'


class CompositeField(object):
    def __init__(self, layout=None):
        self.layout = layout or {}

    def parse(self, row):
        record = {}

        for key in self.layout:
            record[key] = self.layout[key].parse(row)

        # FIXME: still return when we have value int(0)
        if any([record[key] for key in record]):
            return record


class TagField(CharField):
    def _clean(self, title):
        return title.lower().replace('-', ' ').replace('\'s', '').replace(u'’s', '')

    def _guess_tag(self, title):
        KEYWORD_TYPE_MAP = OrderedDict({
            'audio': 'Audio',
            'video': 'Video',
            'arrest report': 'AR',
            'officer battery report': 'OBR',
            'original case incident report': 'OCIR',
            'tactical response report': 'TRR',
            'case report': 'CR',
        })
        cleaned_title = self._clean(title)

        for keyword, document_type in KEYWORD_TYPE_MAP.items():
            if keyword in cleaned_title:
                return document_type

        return 'Other'

    def parse(self, row):
        title = row.get(self.field_name, '')
        document_type = self._guess_tag(title)

        return document_type


class PortalAttachmentFileField(object):
    def parse(self, record):
        schema = CompositeField(layout={
            'file_type': MediaTypeField(field_name='type'),
            'title': CharField(field_name='title'),
            'url': CharField(field_name='link'),
            'original_url': CharField(field_name='link'),
            'tag': TagField(field_name='title'),
            'source_type': Just(AttachmentSourceType.PORTAL_COPA),
            'external_last_updated': DateTimeField(field_name='last_updated'),
        })
        return schema.parse(record)


class SummaryReportsAttachmentFileField(object):
    def parse(self, record):
        schema = CompositeField(layout={
            'file_type': Just(MEDIA_TYPE_DOCUMENT),
            'url': CharField(field_name='link'),
            'original_url': CharField(field_name='link'),
            'source_type': Just(AttachmentSourceType.SUMMARY_REPORTS_COPA),
            'external_last_updated': DateTimeField(field_name='last_updated'),
        })
        return schema.parse(record)


class ArraySourceField(object):
    def __init__(self, field_name, parser):
        self.field_name = field_name
        self.parser = parser

    def parse(self, row):
        values = row.get(self.field_name, [])
        return [self.parser.parse(value) for value in values]


class NotSupportedDateFormatException(Exception):
    pass


class DateTimeField(SimpleField):
    DATE_SUPPORTED_PATTERNS = ['%m-%d-%Y %I:%M %p', '%B %d, %Y']

    def parse(self, row):
        value = row.get(self.field_name, '')

        if not value:
            return None

        for pattern in self.DATE_SUPPORTED_PATTERNS:
            try:
                return datetime.strptime(value, pattern).replace(tzinfo=pytz.utc)
            except ValueError:
                pass

        try:
            return iso8601.parse_date(value)
        except iso8601.ParseError:
            pass

        raise NotSupportedDateFormatException(value)
