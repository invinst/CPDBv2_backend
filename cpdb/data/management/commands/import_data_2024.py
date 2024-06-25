from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Calls other Django commands'

    def handle(self, *args, **options):

        # Call other Django commands with the file_path argument
        try:
            # execute migrations
            call_command('migrate')
            print("Officers")
            file_path = "/usr/src/app/cpdb/data-updates/officers/final-profiles.csv"
            call_command('import_officer_data_2024', file_path=file_path)

            print("Complaints-Complaints")
            file_path = "/usr/src/app/cpdb/data-updates/complaints/complaints-complaints.csv"
            call_command('import_complaints_complaints_data_2024', file_path=file_path)

            print("Complaints")
            file_path = "/usr/src/app/cpdb/data-updates/complaints/complainants.csv"
            call_command('import_complaints_data_2024', file_path=file_path)

            print("Complaints Accused")
            file_path = "/usr/src/app/cpdb/data-updates/complaints/complaints-accused.csv"
            call_command('import_complaints_accused_data_2024', file_path=file_path)

            print("Witness")
            file_path = "/usr/src/app/cpdb/data-updates/complaints/civilian_witnesses.csv"
            call_command('import_complaints_data_2024', file_path=file_path)

            print("Investigators")
            file_path = "/usr/src/app/cpdb/data-updates/complaints/investigators.csv"
            call_command('import_investigators_data_2024', file_path=file_path)

            print("Victims")
            file_path = "/usr/src/app/cpdb/data-updates/complaints/victims.csv"
            call_command('import_victims_data_2024', file_path=file_path)

            print("TRR Main")
            file_path = "/usr/src/app/cpdb/data-updates/trrs/trr_main.csv"
            call_command('import_trr_trr_data_2024', file_path=file_path)

            print("TRR action responses")
            file_path = "/usr/src/app/cpdb/data-updates/trrs/trr_actions_responses-1.csv"
            call_command('import_trr_action_responses_data_2024', file_path=file_path)
            file_path = "/usr/src/app/cpdb/data-updates/trrs/trr_actions_responses-2.csv"
            call_command('import_trr_action_responses_data_2024', file_path=file_path)
            file_path = "/usr/src/app/cpdb/data-updates/trrs/trr_actions_responses-3.csv"
            call_command('import_trr_action_responses_data_2024', file_path=file_path)

            print("TRR statuses")
            file_path = "/usr/src/app/cpdb/data-updates/trrs/trr_statuses.csv"
            call_command('import_trr_statuses_data_2024', file_path=file_path)

            print("Subject weapons")
            file_path = "/usr/src/app/cpdb/data-updates/trrs/trr_subject_weapons.csv"
            call_command('import_subjectweapon_data_2024', file_path=file_path)

            print("weapons discharges")
            file_path = "/usr/src/app/cpdb/data-updates/trrs/trr_weapon_discharges.csv"
            call_command('import_weapondischarge_data_2024', file_path=file_path)

            print("Awards")
            file_path = "/usr/src/app/cpdb/data-updates/awards/awards.csv"
            call_command('import_awards_data_2024', file_path=file_path)

            print("Salaries")
            file_path = "/usr/src/app/cpdb/data-updates/salaries/salaries.csv"
            call_command('import_salaries_data_2024', file_path=file_path)

            print("Settlemnts")
            file_path = "/usr/src/app/cpdb/data-updates/settlements/settlements.csv"
            call_command('import_settlement_data_2024', file_path=file_path)

            print("Unit History")
            file_path = "/usr/src/app/cpdb/data-updates/unit_histories/unit-history.csv"
            call_command('import_unit_data_2024', file_path=file_path)

            print("Generating cache")
            call_command('cache_data')

            # Add more calls to other commands as needed
        except CommandError as e:
            self.stderr.write(f"Error: {e}")
