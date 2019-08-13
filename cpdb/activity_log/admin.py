from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Count, Q

from activity_log.constants import ADD_TAG_TO_DOCUMENT, REMOVE_TAG_FROM_DOCUMENT


class DocumentTagsAnalyze(User):
    class Meta:
        proxy = True


class DocumentTagsAnalyzeAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'added_tags_count', 'removed_tags_count']

    def get_queryset(self, request):
        return User.objects.annotate(
            added_tags_count=Count('activitylog', filter=Q(activitylog__action_type=ADD_TAG_TO_DOCUMENT))
        ).annotate(
            removed_tags_count=Count('activitylog', filter=Q(activitylog__action_type=REMOVE_TAG_FROM_DOCUMENT))
        )

    def added_tags_count(self, user):
        return user.added_tags_count

    def removed_tags_count(self, user):
        return user.removed_tags_count

    added_tags_count.admin_order_field = 'added_tags_count'
    removed_tags_count.admin_order_field = 'removed_tags_count'


admin.site.register(DocumentTagsAnalyze, DocumentTagsAnalyzeAdmin)
