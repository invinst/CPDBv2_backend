from django.contrib import admin
from .models import AttachmentRequest


class AttachmentRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'timestamp', 'is_being_investigated')
    fields = readonly_fields = ('email', 'crid', 'timestamp', 'investigator_names')

    def has_add_permission(self, request):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


admin.site.register(AttachmentRequest, AttachmentRequestAdmin)
