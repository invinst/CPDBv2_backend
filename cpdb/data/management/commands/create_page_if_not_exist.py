from django.core.management import BaseCommand

from wagtail.wagtailcore.models import Page

from data.utils import get_model


class Command(BaseCommand):
    help = 'Create page with prodived model and title if none exist'

    def add_arguments(self, parser):
        parser.add_argument('model_name', type=str, help='Model to create if no instance exist')
        parser.add_argument('title', type=str, help='Title to give to model instance if one is created')

    def handle(self, *args, **options):
        self.create_page(options['model_name'], options['title'])

    def create_page(self, model_name, title):
        Model = get_model(model_name)
        if Model.objects.first() is None:
            root = Page.objects.first()
            page = root.add_child(instance=Model(title=title))
            self.stdout.write('pk just created: %d' % page.pk)
        else:
            self.stdout.write('existing pk: %d' % Model.objects.first().pk)
