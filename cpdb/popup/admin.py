from django.contrib import admin
from django.contrib.admin import ModelAdmin

from popup.models import Popup


class PopupAdmin(ModelAdmin):
    list_display = ('name', 'page', 'title', 'text')


admin.site.register(Popup, PopupAdmin)
