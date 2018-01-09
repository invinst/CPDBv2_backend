from django.contrib import admin
from .models import AppliedFixture


@admin.register(AppliedFixture)
class AppliedFixtureAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'created')
