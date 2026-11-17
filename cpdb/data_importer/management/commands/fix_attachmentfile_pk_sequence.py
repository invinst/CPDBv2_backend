"""
Re-sync the PostgreSQL sequence for data_attachmentfile.id.

Run this after bulk loads, restores, or manual SQL that can leave the sequence
behind the actual MAX(id), which causes:

    IntegrityError: duplicate key value violates unique constraint "data_attachmentfile_pkey"

when Django inserts new AttachmentFile rows.
"""
from django.core.management.base import BaseCommand
from django.db import connection

from data.models import AttachmentFile


class Command(BaseCommand):
    help = 'Reset data_attachmentfile id sequence to MAX(id) (PostgreSQL only).'

    def handle(self, *args, **options):
        if connection.vendor != 'postgresql':
            self.stderr.write(self.style.ERROR('This command only supports PostgreSQL.'))
            return

        table = AttachmentFile._meta.db_table
        with connection.cursor() as cursor:
            # table comes from Django model meta (not user input)
            cursor.execute(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('{table}', 'id'),
                    COALESCE((SELECT MAX(id) FROM "{table}"), 0)
                )
                """
            )
            new_val = cursor.fetchone()[0]

        self.stdout.write(
            self.style.SUCCESS(
                f'{table}.id sequence updated; next id will be > {new_val}'
            )
        )
