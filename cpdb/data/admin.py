from django.contrib import admin
from .models import AttachmentRequest


class AttachmentRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at', 'investigated_by_cpd')
    fields = readonly_fields = ('email', 'crid', 'created_at', 'investigated_by_cpd', 'investigator_names')

    def has_add_permission(self, request):
        return False  # pragma: no cover


admin.site.register(AttachmentRequest, AttachmentRequestAdmin)
