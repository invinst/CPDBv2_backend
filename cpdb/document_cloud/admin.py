from django.contrib import admin
from .models import DocumentCrawler, DocumentCloudSearchQuery


class DocumentCrawlerAdmin(admin.ModelAdmin):
    readonly_fields = list_display = (
        'id', 'source_type', 'num_documents', 'num_new_documents', 'num_updated_documents', 'created_at'
    )

    def has_add_permission(self, request):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


class DocumentCloudSearchQueryAdmin(admin.ModelAdmin):
    list_display = ('id', 'query', 'type')


admin.site.register(DocumentCrawler, DocumentCrawlerAdmin)
admin.site.register(DocumentCloudSearchQuery, DocumentCloudSearchQueryAdmin)
