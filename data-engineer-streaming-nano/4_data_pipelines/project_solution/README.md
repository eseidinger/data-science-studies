# Data Pipelines

## Instructions

The project consists of following files

* *create_tables.sql* : create the staging and final tables
* *plugin/helpers/sql_queries.py* : SQL select statements to fill transform data and load final tables
* *plugin/operators/stage_redshift.py* : Operator to load data from S3 and stage into Redshift tables
* *plugin/operators/load_fact.py* : Operator to transform data from the staging tables and load into facts table
* *plugin/operators/load_dimension.py* : Operator to transform data from the staging tables and load into dimension table
* *plugin/operators/data_quality.py* : Operator to perform quality checks on the final tables
* *dags/udac_example_dag.py* : DAG to perform ETL on the Sparkify data using the above operators

### Perform ETL

* Run create_tables.sql on a Redshift database
* Configure aws_credentials and redshift connection in Apache Airflow
* Import the DAG and the plugins into Apache Airflow
* Run the DAG

## Purpose of the database

The purpose of the database is to gain insight about the users of Sparkify and their listening habits. Information is
extracted from song data files and log data which contains actions of users on the songs.

## Database schema design

The database schema is a star schema centered around the songplays facts table. The songplays table contains information
about "next song" events including a timestamp and foreign keys to the dimension tables.  
There are dimension tables for users, songs, artist and time.   
The tables can be joined to make queries about the listening habits of the users.
