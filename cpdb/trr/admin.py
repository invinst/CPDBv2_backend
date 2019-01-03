from django.contrib import admin
from .models import TRRAttachmentRequest


class TRRAttachmentRequestAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    fields = readonly_fields = ('email', 'trr_id', 'created_at')


admin.site.register(TRRAttachmentRequest, TRRAttachmentRequestAdmin)
