from django.contrib import admin
from .models import AttachmentRequest


class AttachmentRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'timestamp', 'investigated_by_cpd')
    fields = readonly_fields = ('email', 'crid', 'timestamp', 'investigated_by_cpd', 'investigator_names')

    def has_add_permission(self, request):
        return False  # pragma: no cover

    def get_queryset(self, request):
        return AttachmentRequest.objects.annotate_investigated_by_cpd().select_related('allegation')

    def investigated_by_cpd(self, obj):
        return obj.investigated_by_cpd
    investigated_by_cpd.boolean = True


admin.site.register(AttachmentRequest, AttachmentRequestAdmin)
