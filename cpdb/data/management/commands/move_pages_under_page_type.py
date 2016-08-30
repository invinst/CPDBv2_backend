from django.core.management import BaseCommand

from tqdm import tqdm

from data.utils import get_model


# This class has no test because we can't make a test that pass.
# Something in django treebeard behave weird when running tests.
class Command(BaseCommand):  # pragma: no cover
    help = 'Move all pages of certain type to under one page'

    def add_arguments(self, parser):
        parser.add_argument('child_model', type=str, help='Page type to move')
        parser.add_argument('parent_model', type=str, help='Target model')
        parser.add_argument('parent_id', type=int, help='Target model id')

    def handle(self, *args, **options):
        self.move_pages(options['parent_model'], options['child_model'], options['parent_id'])

    def move_pages(self, parent_model, child_model, parent_id):
        ParentModel = get_model(parent_model)
        ChildModel = get_model(child_model)
        parent_node = ParentModel.objects.get(pk=parent_id)

        for child_node in tqdm(ChildModel.objects.all(), desc='Moving'):
            child_node.move(parent_node, pos='last-child')

        self.stdout.write('%d pages moved' % ChildModel.objects.count())
