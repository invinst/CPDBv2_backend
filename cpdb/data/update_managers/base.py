from django.db import transaction
from django.db import connection
from django.db import models
from tqdm import tqdm
from typing import Type
from rest_framework import serializers


class UpdateManagerBase:
    """
    A base class for managing updates to a database table from a file.

    In most cases, subclasses should provide a serializer (for validation, since this is using bulk create),
    and implement a query_data method to query the data from the holding table.

    Generally as much processing as possible should be done in the database for efficiency, but if there is
    additional processing that needs to be done in Python, it can be done in preprocess_batch.

    Finally, in some cases where related models need to be updated, simply overwrite process_batch

    Attributes:
        table_name (str): The name of the holding table for the data.
        filename (str): The name of the file containing the data to update. Should be in data-updates/ folder.
        Model (models.Model): The Django model representing the database table.
        Serializer (serializers.Serializer): The serializer for validating and deserializing the data.
        batch_size (int): The number of records to process in each batch.
        offset (int): The starting point for processing records.
        row_count (int): The total number of rows processed.

    Methods:
        delete_existing_data(): Deletes all existing data in the table, should cascade delete.
        query_data(): Abstract method to query data, must be implemented by subclasses.
        preprocess_batch(batch): Preprocesses a batch of data before processing.
        process_batch(batch): Processes a batch of data and inserts it into the database.
        update_data(update_holding_table=False): Updates the database table with data from the file.
    """
    def __init__(self, table_name: str, filename: str,
                 Model: Type[models.Model], Serializer: Type[serializers.ModelSerializer],
                 batch_size: int):
        self.table_name = table_name
        self.filename = filename

        self.Model = Model
        self.Serializer = Serializer

        self.model_name = Model._meta.model_name

        self.offset = 0
        self.batch_size = batch_size

    def delete_existing_data(self):
        # TODO: Implement cascade delete in a more efficient way, this is slow
        # but necessarily so for now: django does not put cascade delete on foreign keys in the database.
        # since we're basically truncating the whole table on updates,
        # look into recursively finding related tables from the schema
        # then deleting from those in sql
        self.Model.objects.all().delete()

    def query_data(self):
        # TODO: change this to give a base query that can then be select count(*) and offset limitted from
        raise NotImplementedError()

    def preprocess_batch(self, batch):
        return batch

    def process_batch(self, batch):
        serializer = self.Serializer(data=batch, many=True)

        # TODO: improve error handling, should only show unique execptions
        # maybe an example and counts
        if serializer.is_valid(raise_exception=True):
            self.Model.objects.bulk_create([self.Model(**d)
                                            for d in batch])

    @transaction.atomic
    def update_data(self, update_holding_table=False):
        cursor = connection.cursor()

        if update_holding_table:
            print(f"Updating holding table {self.table_name}")
            updated_table = self.update_holding_table()
            print(f"Updated holding table {updated_table}")

        cursor.execute(f"select count(*) from {self.table_name}")
        row_count = cursor.fetchone()[0]

        print(f"Deleting existing {self.model_name} data and linked data")
        self.delete_existing_data()

        print(f"Total rows: {row_count}")

        with tqdm(total=row_count, desc=f"Updating {self.model_name} data", unit=" rows") as pbar:
            while self.offset < row_count:
                cursor.execute(self.query_data())
                self.columns = [col[0] for col in cursor.description]
                batch = [dict(zip(self.columns, data)) for data in cursor.fetchall()]

                batch = self.preprocess_batch(batch)
                self.process_batch(batch)

                self.offset += self.batch_size
                pbar.update(len(batch))

        print(f"Finished updating {self.model_name} data")

    @transaction.atomic
    def update_holding_table(self):
        """Updates holding table with data from given filename csv
            makes every column text type for holding
        """
        with open(self.filename, 'r') as f:
            header = f.readline().strip()
            f.seek(0)
            with connection.cursor() as cursor:
                cursor.execute(f"drop table if exists {self.table_name}")

                cursor.execute(f"""create table {self.table_name} (
                                    {', '.join([f"{column} text" for column in header.split(',')])}
                                )""")

                cursor.copy_expert(f"copy {self.table_name} from stdin with csv header", f)

        return f"{self.table_name}"
