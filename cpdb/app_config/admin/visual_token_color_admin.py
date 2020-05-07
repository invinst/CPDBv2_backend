from django.contrib import admin
from app_config.models import VisualTokenColor


class VisualTokenColorAdmin(admin.ModelAdmin):
    list_display = ('lower_range', 'upper_range', 'color', 'text_color')
    fields = (
        'lower_range', 'upper_range', 'color', 'text_color'
    )

    def get_queryset(self, request):
        queryset = super(VisualTokenColorAdmin, self).get_queryset(request)
        return queryset.order_by('lower_range')


admin.site.register(VisualTokenColor, VisualTokenColorAdmin)
