# Updating CPDP Data from CSV Files
This README outlines how to update data for CPDP, by replacing existing data with data given by csv files. 

## Usage 
### Setup
- Ensure that the updated csv files are present at `cpdb/data-updates`
- Update the .env file in the root directory with the relevant database being updated. It should look like: 
```
DB_HOST=server_name_here
DB_NAME=db_name_here
DB_USER=db_username_here
DB_PASSWORD=db_password_here
```

### Full Data Update
In the root directory of the project run:
`docker compose exec web python cpdb/manage.py update_data --all`

Note: this will also run the update_cache function. 

### Single Table Update
To update just a single table/model, feed the model in as a parameter, i.e., 
`docker compose exec web python cpdb/manage.py update_data --model=OfficerAllegation`

Note: this will not automatically run the update_cache function, even if that would be warranted. 

### Update Cache 
To update the cache manually, run:
`docker compose exec web python cpdp/manage.py cache_data`

## Outline of How it Works
* CSV files are read in and bulk inserted to holding tables, with every field treated as a string for speed
* Existing model data, and associated model data, is deleted. 
* The code queries from the holding table, defining data types in the query itself, and constructs model objects from it
* A serializer runs basic field validations, then inserts objects. 

The naive implementation of just reading through each row of the CSV, constructing an object and running validations, then inserting that object is prohibitively slow. This approach allows for a good balance between performance and safety, exploiting the speed of postgres's fast copy, and the general speedup of doing operations in SQL rather than ORM objects, while still using a serializer for validations for safety.

## Implementation 

A base class in `cpdb/update_managers/base.py` generically defines how an update works, and each of the models gets its own subclass with a model specific implementation in the same folder, e.g., `cpdb/update_managers/update_officer_manage.py` defines updating officer data. 

A subclass of the base class really only needs the following 2 things implemented to be fully functional: 
- a serializer, which is used for model validation for objects before inserting them
- a query, which is a SQL query that attempts to do as much of the required data processing as possible for the sake of efficiency

The main method is the "update_data" method, which does the following in order: 
* updates the csv holding table
* deletes existing data, as well as existing associated data (all officer data if deleting officers, for example)
* queries the holding table with the given query method, which does as much data processing as possible
* gets one batch_size worth of data with that query
* runs optional in-python processing
* run model validations in bulk through the given serializer, which constructs model objects
* inserts that batch, repeats until all data is inserted

Subclasses will often add preprocessing steps to insert related data, such as inserting OfficerBadgeNumber objects when inserting new Officer objects. 