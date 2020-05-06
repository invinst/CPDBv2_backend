from django.contrib import admin
from app_config.models import AppConfig


class AppConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'description')
    fields = (
        'name', 'value', 'description'
    )
    readonly_fields = ['name', 'description']

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(AppConfig, AppConfigAdmin)
