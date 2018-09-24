from django.contrib import admin
from .models import AttachmentRequest


class AttachmentRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'timestamp')
    fields = readonly_fields = ('email', 'crid', 'timestamp')

    def has_add_permission(self, request):
        return False  # pragma: no cover


admin.site.register(AttachmentRequest, AttachmentRequestAdmin)
