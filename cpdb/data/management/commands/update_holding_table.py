from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction


class Command(BaseCommand):
    help = 'Updates holding tables with data from csvs'

    def add_arguments(self, parser):
        parser.add_argument('--filename',
                            help='Path of csv file from data-updates/ folder. E.g. --filename=trr/trr_main.csv')

    def handle(self, *args, **options):
        filename = options.get('filename')

        if not filename:
            self.print_help('manage.py', 'update_holding_table')
            raise CommandError("filename is a required argument")
        elif not filename.endswith('.csv'):
            raise CommandError("filename must be a csv file")

        table_name = self.update_holding_table(f"data-updates/{filename}")
        print(f"Finished updating holding table {table_name}")

    @transaction.atomic
    def update_holding_table(self, filename):
        """Updates holding table with data from given filename csv
            makes every column text type for holding
        """
        table_name = filename.split('/')[-1].split('.')[0].replace("-", "_")

        with open(filename, 'r') as f:
            header = f.readline().strip()
            f.seek(0)
            with connection.cursor() as cursor:
                cursor.execute(f"drop table if exists csv_{table_name}")

                cursor.execute(f"""create table csv_{table_name} (
                                    {', '.join([f"{column} text" for column in header.split(',')])}
                                )""")

                cursor.copy_expert(f"copy csv_{table_name} from stdin with csv header", f)

        return f"csv_{table_name}"
