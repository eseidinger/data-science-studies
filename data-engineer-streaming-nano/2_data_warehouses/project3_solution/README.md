# Data Warehouse

## Instructions

The project consists of three Python scripts and a configuration file.

* *create_tables.py* : initialize staging and final tables
* *etl.py* : perform ETL
* *sql_queries.py* : queries used by the above scripts
* *dwh_template.cfg* : template file for AWS connection data

### Configure connection

Rename *dwh_template.cfg* to *dwh.cfg* and fill in connection data.

### Initialize the tables

    python create_tables.py

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

    SELECT COUNT(weekday), weekday
    FROM songplays, time 
    WHERE songplays.start_time = time.start_time
    GROUP BY weekday
    ORDER BY COUNT(weekday);

The query above gives following result:

|count|weekday|
|-----|-------|
|58   |0      |
|90   |6      |
|160  |4      |
|188  |5      |
|191  |2      |
|207  |1      |
|250  |3      |

At the weekend there are the fewer songplay events. This leads to the conclusion that most people listen to music while
at work.
