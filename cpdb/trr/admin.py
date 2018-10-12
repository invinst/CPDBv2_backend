from django.contrib import admin
from .models import TRRAttachmentRequest


class TRRAttachmentRequestAdmin(admin.ModelAdmin):
    list_display = ['__unicode__']
    fields = readonly_fields = ('email', 'trr_id', 'timestamp')


admin.site.register(TRRAttachmentRequest, TRRAttachmentRequestAdmin)
