# Data Modeling with Postgres

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
|396  |6      |
|630  |5      |
|1014 |0      |
|1054 |3      |
|1073 |1      |
|1297 |4      |
|1370 |2      |

At the weekend there are the fewer songplay events. This leads to the conclusion that most people listen to music while
at work.
