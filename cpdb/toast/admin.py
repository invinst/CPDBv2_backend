from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import CharField
from django.forms import TextInput

from toast.models import Toast


class ToastAdmin(ModelAdmin):
    list_display = ('name', 'template', 'tags')

    formfield_overrides = {
        CharField: {'widget': TextInput(attrs={'size': '101'})},
    }


admin.site.register(Toast, ToastAdmin)
