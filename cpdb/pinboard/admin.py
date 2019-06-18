from django.contrib import admin
from django.db.models import Q

from .models import ExamplePinboard, Pinboard


class PinboardAdmin(admin.ModelAdmin):
    fields = ['id', 'title', 'description', 'officers', 'allegations', 'trrs']
    list_display = ['id', 'title', 'description']
    readonly_fields = ['id', 'officers', 'allegations', 'trrs']
    search_fields = ['id', 'title']

    def get_search_results(self, request, queryset, search_term):
        query_set = self.model.objects.all()

        if search_term:
            title_query = Q(title__icontains=search_term)
            try:
                int(search_term, 16)
                id_query = Q(id__lte=search_term.ljust(8, 'f'), id__gte=search_term.ljust(8, '0'))
                query_set = query_set.filter(id_query | title_query)
            except ValueError:
                query_set = query_set.filter(title_query)

        return query_set, True


class ExamplePinboardAdmin(admin.ModelAdmin):
    autocomplete_fields = ['pinboard']


admin.site.register(Pinboard, PinboardAdmin)
admin.site.register(ExamplePinboard, ExamplePinboardAdmin)
