from django.contrib import admin

from data.models import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(Tag, TagAdmin)
