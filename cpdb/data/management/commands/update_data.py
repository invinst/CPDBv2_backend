from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from data import update_managers


class Command(BaseCommand):
    help = 'Bulk updates data from csv files in data-updates/. NOTE: deletes ALL existing data, use with caution.'

    def add_arguments(self, parser):
        parser.add_argument('--model',
                            type=str,
                            help='Model name to update, e.g., --model=OfficerAllegation')
        parser.add_argument('--all',
                            action='store_true',
                            help='Update all models')

        parser.add_argument('--batch_size',
                            type=int,
                            help='Batch size for updating data',
                            default=10000)

        parser.add_argument('--update_holding_table',
                            action='store_true',
                            help='Update holding table with data from csv file',
                            default=True)

    def handle(self, *args, **options):
        model = options.get('model')
        all = options.get('all')
        batch_size = options.get('batch_size')
        update_holding_table = options.get('update_holding_table')

        if all:
            update_managers.update_all(batch_size=batch_size, update_holding_table=update_holding_table)
            call_command('cache_data')

        elif model:
            update_manager = update_managers.get(model)(batch_size=batch_size)

            if update_manager:
                update_manager.update_data(update_holding_table=update_holding_table)
            else:
                raise CommandError(f"Model {model} not found in update managers.")
        else:
            self.print_help('manage.py', 'update_data')
            raise CommandError("either all flag or model is a required argument")
