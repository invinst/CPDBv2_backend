from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Calls other Django commands'

    def handle(self, *args, **options):

        # Call other Django commands with the table_name argument
        try:
            # execute migrations
            # call_command('migrate')
            # print("Officers")
            # table_name = "csv_officer"
            # call_command('import_officer_data_2024', table_name=table_name)
            #
            # print("Complaints-Complaints")
            # table_name = "csv_complaints_complaints"
            # call_command('import_complaints_complaints_data_2024', table_name=table_name)
            #
            # print("Complaints")
            # table_name = "csv_complaints"
            # call_command('import_complaints_data_2024', table_name=table_name)
            #
            # print("Complaints Accused")
            # table_name = "csv_complaints_accused"
            # call_command('import_complaints_accused_data_2024', table_name=table_name)
            #
            # print("Witness")
            # table_name = "csv_civilian_witnesses"
            # call_command('import_complaints_data_2024', table_name=table_name)
            #
            # print("Investigators")
            # table_name = "csv_investigators"
            # call_command('import_investigators_data_2024', table_name=table_name)

            print("Victims")
            table_name = "csv_victims"
            call_command('import_victims_data_2024', table_name=table_name)

            print("TRR Main")
            table_name = "csv_trr_main"
            call_command('import_trr_trr_data_2024', table_name=table_name)

            print("TRR action responses")
            table_name = "csv_trr_actions_responses"
            call_command('import_trr_action_responses_data_2024', table_name=table_name)

            print("TRR statuses")
            table_name = "csv_trr_statuses"
            call_command('import_trr_statuses_data_2024', table_name=table_name)

            print("Subject weapons")
            table_name = "csv_trr_subject_weapons"
            call_command('import_subjectweapon_data_2024', table_name=table_name)

            print("weapons discharges")
            table_name = "csv_trr_weapon_discharges"
            call_command('import_weapondischarge_data_2024', table_name=table_name)

            print("Awards")
            table_name = "csv_awards"
            call_command('import_awards_data_2024', table_name=table_name)

            print("Salaries")
            table_name = "csv_salaries"
            call_command('import_salaries_data_2024', table_name=table_name)

            print("Settlemnts")
            table_name = "csv_settlements"
            call_command('import_settlement_data_2024', table_name=table_name)

            print("Unit History")
            table_name = "csv_units"
            call_command('import_unit_data_2024', table_name=table_name)
            #
            print("Generating cache")
            call_command('cache_data')

            # Add more calls to other commands as needed
        except CommandError as e:
            self.stderr.write(f"Error: {e}")
