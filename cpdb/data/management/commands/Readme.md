# Import Data 2024 Command

This Django management command, `import_data_2024.py`, is designed to streamline the process of importing various data
sets into your Django application. It sequentially calls other custom management commands, each responsible for importing
specific data files into the database.

## Prerequisites

- Django installed in your project
- Custom Django management commands for importing data
- Data files located in the specified paths

## File Structure

Ensure your project directory has the following structure:

```
project/
│
├── manage.py
├── app/
│   ├── management/
│   │   ├── commands/
│   │   │   ├── import_data_2024.py
│   │   │   ├── import_officer_data_2024.py
│   │   │   ├── import_complaints_complaints_data_2024.py
│   │   │   ├── import_complaints_data_2024.py
│   │   │   ├── import_complaints_accused_data_2024.py
│   │   │   ├── import_investigators_data_2024.py
│   │   │   ├── import_victims_data_2024.py
│   │   │   ├── import_trr_trr_data_2024.py
│   │   │   ├── import_trr_action_responses_data_2024.py
│   │   │   ├── import_trr_statuses_data_2024.py
│   │   │   ├── import_subjectweapon_data_2024.py
│   │   │   ├── import_weapondischarge_data_2024.py
│   │   │   ├── import_awards_data_2024.py
│   │   │   ├── import_salaries_data_2024.py
│   │   │   ├── import_settlement_data_2024.py
│   │   │   ├── import_unit_data_2024.py
│   │   └── __init__.py
│   └── __init__.py
└── data-updates/
    ├── officers/
    │   └── final-profiles.csv
    ├── complaints/
    │   ├── complaints-complaints.csv
    │   ├── complainants.csv
    │   ├── complaints-accused.csv
    │   ├── civilian_witnesses.csv
    │   ├── investigators.csv
    │   └── victims.csv
    ├── trrs/
    │   ├── trr_main.csv
    │   ├── trr_actions_responses.csv
    │   ├── trr_statuses.csv
    │   ├── trr_subject_weapons.csv
    │   └── trr_weapon_discharges.csv
    ├── awards/
    │   └── awards.csv
    ├── salaries/
    │   └── salaries.csv
    └── settlements/
        └── settlements.csv
```

## Usage

To execute the `import_data_2024.py` command, run the following command in your terminal from your project directory:

```sh
python manage.py import_data_2024
```

## Command Description

This command performs the following tasks in sequence:

1. **Migrations**:
   - Executes Django migrations to ensure the database schema is up-to-date.

2. **Data Imports**:
   - **Officers**: Imports officer data from `final-profiles.csv`.
   - **Complaints**: Imports complaints data from multiple CSV files.
     - `complaints-complaints.csv`
     - `complainants.csv`
     - `complaints-accused.csv`
     - `civilian_witnesses.csv`
     - `investigators.csv`
     - `victims.csv`
   - **TRRs**: Imports Tactical Response Reports (TRR) data from multiple CSV files.
     - `trr_main.csv`
     - `trr_actions_responses.csv`
     - `trr_statuses.csv`
     - `trr_subject_weapons.csv`
     - `trr_weapon_discharges.csv`
   - **Awards**: Imports awards data from `awards.csv`.
   - **Salaries**: Imports salaries data from `salaries.csv`.
   - **Settlements**: Imports settlements data from `settlements.csv`.
   - **Unit History**: Imports unit history data from `unit-history.csv`.

3. **Cache Generation**:
   - Generates cache data by calling the `cache_data` command.

## Error Handling

If an error occurs during the execution of any command, it will be caught and displayed in the terminal.

## Customization

You can customize or extend the `import_data_2024.py` command by adding more calls to `call_command` with appropriate file paths and custom commands as needed.

```python
# Add more calls to other commands as needed
file_path = "path_to_your_file.csv"
call_command('your_custom_command', file_path=file_path)
```
