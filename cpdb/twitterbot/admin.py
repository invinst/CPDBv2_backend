from django.contrib import admin

from .models import ResponseTemplate, TwitterBotResponseLog


@admin.register(ResponseTemplate)
class ResponseTemplateAdmin(admin.ModelAdmin):
    list_display = ('syntax', 'response_type')
    list_filter = ('response_type',)
    search_fields = ('syntax',)


@admin.register(TwitterBotResponseLog)
class TwitterBotResponseLogAdmin(admin.ModelAdmin):
    list_display = (
        'tweet_content', 'tweet_url', 'created_at', 'sources', 'entity_url', 'incoming_tweet_url',
        'incoming_tweet_username', 'incoming_tweet_content', 'original_tweet_url', 'original_tweet_username',
        'original_tweet_content')
