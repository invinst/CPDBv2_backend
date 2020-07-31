from django.contrib import admin, contenttypes
from django import forms
from documentcloud import DocumentCloud
from django.conf import settings

from data.constants import MEDIA_TYPE_DOCUMENT, AttachmentSourceType
from document_cloud.utils import parse_id, get_url
from data.models import Officer, AttachmentFile


class OfficerForm(forms.ModelForm):
    attachment = forms.FileField()
    attachment_title = forms.CharField()

    class Meta:
        model = Officer
        fields = '__all__'

    def save(self, commit=True):
        client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)
        attachment = self.cleaned_data.get('attachment', None)
        attachment_title = self.cleaned_data.get('attachment_title', None)

        cloud_document = client.documents.upload(
            attachment.file,
            title=attachment_title,
            description='Manual upload',
            access='public',
            force_ocr=True
        )

        officer = super(OfficerForm, self).save(commit=False)
        url = get_url(cloud_document)

        new_attachment = AttachmentFile(
            external_id=parse_id(cloud_document.id),
            owner=officer,
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            title=cloud_document.title,
            url=url,
            file_type=MEDIA_TYPE_DOCUMENT,
            original_url=url,
            preview_image_url=cloud_document.normal_image_url,
            external_created_at=cloud_document.created_at,
            external_last_updated=cloud_document.updated_at,
            text_content='',
            pages=cloud_document.pages
        )

        new_attachment.save()
        return officer


class AttachmentFileInline(contenttypes.admin.GenericStackedInline):
    model = AttachmentFile
    extra = 0
    ct_fk_field = 'owner_id'
    ct_field = 'owner_type'
    readonly_fields = fields = [
        'title',
        'url',
    ]

    def has_add_permission(self, request):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


class OfficerAdmin(admin.ModelAdmin):
    inlines = [AttachmentFileInline]
    form = OfficerForm
    list_display = ('id', 'first_name', 'last_name')
    fieldsets = (
        ('Fieldset', {
            'fields': ('first_name', 'last_name', 'attachment_title', 'attachment'),
        }),
    )
    readonly_fields = ('first_name', 'last_name')

    def has_add_permission(self, request):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


admin.site.register(Officer, OfficerAdmin)
