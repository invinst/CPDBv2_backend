from django.contrib import admin
from .models import EmailTemplate


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('type', 'subject', 'from_email')

    def has_add_permission(self, request):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


admin.site.register(EmailTemplate, EmailTemplateAdmin)
