from django.contrib import admin
from django.db.models import Max, Count
from django.urls import reverse
from django.utils.safestring import mark_safe

from data.models import AttachmentFile


def max_tag_count():
    query_set = AttachmentFile.objects.all()
    query_set = query_set.prefetch_related('tags').annotate(tag_count=Count('tags')).aggregate(Max('tag_count'))
    return query_set['tag_count__max']


MAX_ATTACHMENT_TAG_COUNT = max_tag_count()


class AttachmentFileAdmin(admin.ModelAdmin):
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
        'text_content',
        'reprocess_text_count',
        'pages',
        'pending_documentcloud_id',
        'upload_fail_attempts',
        'manually_updated',
        'last_updated_by',
    ]

    def get_list_display(self, request):
        list_display = ['id', 'title', 'source_type', 'updated_at']
        for tag_index in range(0, MAX_ATTACHMENT_TAG_COUNT):
            list_display.append(f'tag_{tag_index}')
        return list_display

    def get_queryset(self, request):
        return AttachmentFile.objects.all().prefetch_related('tags', 'allegation', 'last_updated_by')


def create_tag_field(index):
    def tag_field(self, obj):
        if obj.tags.count() > index:
            tag = obj.tags.all()[index]
            url = reverse('admin:data_tag_change', args=[tag.pk])
            return mark_safe(f'<a href={url}>{tag.name}</a>')
        return ''

    tag_field.allow_tags = True
    tag_field.short_description = f'Tag {index}'

    return tag_field


for i in range(0, MAX_ATTACHMENT_TAG_COUNT):
    setattr(AttachmentFileAdmin, f'tag_{i}', create_tag_field(i))


admin.site.register(AttachmentFile, AttachmentFileAdmin)
