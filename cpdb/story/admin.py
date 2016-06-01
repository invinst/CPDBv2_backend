from django.contrib import admin

from story.models import Newspaper


class NewspaperAdmin(admin.ModelAdmin):
    pass
admin.site.register(Newspaper, NewspaperAdmin)
