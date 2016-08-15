from datetime import datetime, date

from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos.collections import MultiPolygon, Point, MultiLineString

from rest_framework import serializers

from data_versioning.models import Changelog, LOG_TYPE_CREATE, LOG_TYPE_UPDATE, LOG_TYPE_DELETE
from data_versioning.utils import get_many_to_many_fields, get_foreign_key_fields


class PostgreSQLChangeKeeper(object):
    """
    Save all model instances through this object to record changes as well.

    How to record changes:
        change_keeper = PostgreSChangeKeeper()
        # source is freeform, you can put anything in this dict
        # content is just regular properties that you would supply to klass.objects.create
        change_keeper.create(PoliceUnit, source={'name': 'ipra'}, content={'unit_name': '010'})
        change_keeper.update(
            allegation, source={'name': 'FOIA', 'azure_blob_storage_id': 'abc123xyz'},
            content={'city': 'Chicago'})
        change_keeper.delete(officer)

    How to query changes:
        Changelog.objects.filter(target_model='common.officer', object_pk=7617)
        Changelog.objects.filter(log_type=LOG_TYPE_CREATE, created__gte=...)
        # Content and source fields are both JSONField, you can query them within PostgreSQL.
        # Content is not kept in changelog exactly how they were inserted:
        # Foreign key and many to many relation are all transformed into just private keys.
        # For any update changelog, content contains both old and new values of fields that changed.
        # For delete changelog, content contains the object that was deleted

    Known limitations:
    - For now there's no support for when you need to import geo data through LayerMapping
    """

    def _create_objects_in_current_database(self, klass, content, many_to_many_fields):
        instance = klass.objects.create(**content)
        for field_name, objs in many_to_many_fields.items():
            getattr(instance, field_name).add(*objs)
        return instance

    def _json_serialize(self, val):
        if isinstance(val, datetime) or isinstance(val, date):
            return val.isoformat()
        if isinstance(val, MultiPolygon) or isinstance(val, Point) or isinstance(val, MultiLineString):
            return val.__str__()
        return val

    def _create_changelog(self, klass, content, source, log_type, pk):
        content_type = ContentType.objects.get_for_model(klass)
        self._json_serialize(content)
        Changelog.objects.create(
            content=content,
            source=source,
            object_pk=pk,
            log_type=log_type,
            target_model='%s.%s' % (content_type.app_label, content_type.model))

    def create(self, klass, source, content):
        many_to_many_fields = get_many_to_many_fields(klass, content, pop=True)
        foreign_key_fields = get_foreign_key_fields(klass, content)

        instance = self._create_objects_in_current_database(klass, content, many_to_many_fields)

        content = dict(
            list(content.items()) +
            [(key, [obj.pk for obj in objs]) for key, objs in many_to_many_fields.items()]
        )
        for field_name in foreign_key_fields:
            content[field_name] = content[field_name].pk
        content = {
            key: self._json_serialize(val)
            for key, val in content.items()
        }

        self._create_changelog(klass, content, source, log_type=LOG_TYPE_CREATE, pk=instance.pk)

    def update(self, instance, content, source):
        klass = instance.__class__
        many_to_many_fields = get_many_to_many_fields(klass, content)
        foreign_key_fields = get_foreign_key_fields(klass, content)
        diff = {'pk': instance.pk}

        for key, val in content.items():
            if getattr(instance, key) != val:
                old_val = getattr(instance, key)
                if key in foreign_key_fields:
                    diff[key] = (old_val.pk if old_val else None, val.pk)
                elif key in many_to_many_fields:
                    diff[key] = ([item.pk for item in old_val.all()], [item.pk for item in val])
                else:
                    diff[key] = (getattr(instance, key), val)
                diff[key] = (self._json_serialize(diff[key][0]), self._json_serialize(diff[key][1]))

                setattr(instance, key, val)

        instance.save()
        self._create_changelog(klass, diff, source, log_type=LOG_TYPE_UPDATE, pk=instance.pk)

    def delete(self, instance, source):
        klass = instance.__class__

        class klassSerializer(serializers.ModelSerializer):
            class Meta:
                model = klass

        self._create_changelog(klass, klassSerializer(instance).data, source, log_type=LOG_TYPE_DELETE, pk=instance.pk)
        instance.delete()

    # TODO: replicate LayerMapping import functionality to support GEO fields
