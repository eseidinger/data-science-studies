# Data Lakes

## Instructions

The project consists of a Python script and a configuration file.

* *etl.py* : perform ETL
* *dl_template.cfg* : template file for AWS credentials

### Configure connection

Rename *dl_template.cfg* to *dl.cfg* and fill in credentials.

### Perform ETL

    python etl.py

## Purpose of the database

The purpose of the database is to gain insight about the users of Sparkify and their listening habits. Information is
extracted from song data files and log data which contains actions of users on the songs.

## Database schema design

The database schema is a star schema centered around the songplays facts table. The songplays table contains information
about "next song" events including a timestamp and foreign keys to the dimension tables.  
There are dimension tables for users, songs, artist and time.   
The tables can be joined to make queries about the listening habits of the users.

## Example Query

If one wants to find out on which day of the week people listen to music the most, one could use the following query:

    songplays_table.join(time_table, songplays_table.start_time == time_table.start_time) \
        .groupBy('weekday') \
        .agg({'weekday':'count'}) \
        .show()
