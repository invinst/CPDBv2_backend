from django.contrib import admin

from data.models import AttachmentRequest


class AttachmentRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at', 'investigated_by_cpd', 'noti_email_sent')
    readonly_fields = fields = (
        'email', 'crid', 'created_at', 'investigated_by_cpd', 'investigator_names', 'noti_email_sent'
    )

    def has_add_permission(self, request):
        return False  # pragma: no cover

    def get_queryset(self, request):
        return AttachmentRequest.objects.annotate_investigated_by_cpd().select_related('allegation')

    def investigated_by_cpd(self, obj):
        return obj.investigated_by_cpd
    investigated_by_cpd.boolean = True


admin.site.register(AttachmentRequest, AttachmentRequestAdmin)
