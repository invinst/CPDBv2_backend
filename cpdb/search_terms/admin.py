from django.contrib import admin

from adminsortable.admin import SortableAdmin, SortableTabularInline

from .models import SearchTermCategory, SearchTermItem


class SearchTermItemInline(SortableTabularInline):
    model = SearchTermItem
    extra = 1


@admin.register(SearchTermCategory)
class SearchTermCategoryAdmin(SortableAdmin):
    list_display = ('name', 'order_number')
    ordering = ('order_number',)
    inlines = [SearchTermItemInline]


@admin.register(SearchTermItem)
class SearchTermItemAdmin(SortableAdmin):
    list_display = ('slug', 'name', 'category', 'call_to_action_type', 'description', 'order_number')
    list_filter = ('category', 'call_to_action_type')
    search_fields = ('name', 'slug', 'description')
    ordering = ('order_number',)
