from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel


class FAQsPage(Page):
    subpage_types = ['faq.FAQPage']


class FAQPage(Page):
    body = StreamField([
        ('paragraph', blocks.TextBlock())])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body')
    ]
