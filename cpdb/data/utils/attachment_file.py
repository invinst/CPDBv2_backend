from data.constants import MEDIA_IPRA_COPA_HIDING_TAGS, MEDIA_HIDING_TITLES


def filter_attachments(attachment_queryset):
    query = attachment_queryset.exclude(tag__in=MEDIA_IPRA_COPA_HIDING_TAGS)
    for keyword in MEDIA_HIDING_TITLES:
        query = query.exclude(title__icontains=keyword)
    return query
