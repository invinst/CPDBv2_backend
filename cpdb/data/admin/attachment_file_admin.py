from django.contrib.admin import site, SimpleListFilter, ModelAdmin
from django.db.models import Count

from data.models import AttachmentFile


def standardize_field_name(name):
    return name.replace(' ', '_').lower()


def create_tag_field(tag_name):
    def tag_field(self, obj):
        tag_names = [tag_obj.name for tag_obj in list(obj.tags.all())]
        return tag_name in tag_names

    tag_field.allow_tags = True
    tag_field.short_description = f'{standardize_field_name(tag_name)}'
    tag_field.boolean = True

    return tag_field


class TagListFilter(SimpleListFilter):
    title = 'Tags'
    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        filter_by_tags = [[tag, tag] for tag in AttachmentFile.tags.all().order_by('name')]
        return [['tagged', 'Tagged']] + filter_by_tags

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        if self.value() == 'tagged':
            return queryset.filter(tags__isnull=False).distinct()

        return queryset.filter(tags__name=self.value()).distinct()


class AttachmentFileAdmin(ModelAdmin):
    readonly_fields = [
        'external_id',
        'file_type',
        'allegation',
        'tag',
        'source_type',
        'url',
        'additional_info',
        'original_url',
        'views_count',
        'downloads_count',
        'notifications_count',
        'preview_image_url',
        'external_created_at',
        'external_last_updated',
        'reprocess_text_count',
        'pages',
        'pending_documentcloud_id',
        'upload_fail_attempts',
        'manually_updated',
        'last_updated_by',
    ]
    fields = ['tags', 'title'] + readonly_fields
    list_filter = [TagListFilter]

    def get_list_display(self, request):
        list_display = ['id', 'title', 'source_type', 'updated_at']
        for tag in AttachmentFile.tags.all().order_by('name'):
            list_display.append(standardize_field_name(tag.name))
            setattr(AttachmentFileAdmin, f'{standardize_field_name(tag.name)}', create_tag_field(tag.name))
        return list_display

    def get_queryset(self, request):
        return AttachmentFile.objects.all().prefetch_related(
            'tags',
            'allegation',
            'last_updated_by',
            'tags__taggit_taggeditem_items',
            'tags__taggit_taggeditem_items__content_type',
        ).annotate(tags_count=Count('tags')).order_by('-tags_count')


site.register(AttachmentFile, AttachmentFileAdmin)
