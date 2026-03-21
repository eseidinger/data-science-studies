import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "drop table if exists staging_events"
staging_songs_table_drop = "drop table if exists staging_songs"
songplay_table_drop = "drop table if exists songplays"
user_table_drop = "drop table if exists users"
song_table_drop = "drop table if exists songs"
artist_table_drop = "drop table if exists artists"
time_table_drop = "drop table if exists time"

# CREATE TABLES

staging_events_table_create= ("""
create table if not exists staging_events(
artist VARCHAR,
auth VARCHAR,
first_name VARCHAR,
gender VARCHAR,
item_in_session INTEGER,
last_name VARCHAR,
length DOUBLE PRECISION,
level VARCHAR,
location VARCHAR,
methdod VARCHAR,
page VARCHAR,
registration DOUBLE PRECISION,
session_id INTEGER,
song VARCHAR,
status INTEGER,
ts BIGINT,
user_agent VARCHAR,
user_id INTEGER)
""")

staging_songs_table_create = ("""
create table if not exists staging_songs(
num_songs INTEGER,
artist_id VARCHAR,
artist_latitude DOUBLE PRECISION,
artist_longitude DOUBLE PRECISION,
artist_location VARCHAR,
artist_name VARCHAR,
song_id VARCHAR,
title VARCHAR,
duration DOUBLE PRECISION,
year INTEGER)
""")

songplay_table_create = ("""
create table if not exists songplays(
songplay_id INTEGER IDENTITY(0,1) PRIMARY KEY,
start_time TIMESTAMP,
user_id INTEGER,
level VARCHAR,
song_id VARCHAR,
artist_id VARCHAR,
session_id INTEGER,
location VARCHAR,
user_agent VARCHAR)
""")

user_table_create = ("""
create table if not exists users(
user_id INTEGER PRIMARY KEY,
first_name VARCHAR,
last_name VARCHAR,
gender VARCHAR,
level VARCHAR)
""")

song_table_create = ("""
create table if not exists songs(
song_id VARCHAR PRIMARY KEY,
title VARCHAR,
artist_id VARCHAR,
year INTEGER,
duration DOUBLE PRECISION)
""")

artist_table_create = ("""
create table if not exists artists(
artist_id VARCHAR PRIMARY KEY,
name VARCHAR,
location VARCHAR,
latitude DOUBLE PRECISION,
longitude DOUBLE PRECISION)
""")

time_table_create = ("""
create table if not exists time(
start_time TIMESTAMP,
hour INTEGER,
day INTEGER,
week_of_year INTEGER,
month INTEGER,
year INTEGER,
weekday INTEGER)
""")

# STAGING TABLES

staging_events_copy = ("""
    copy staging_events from '{}'
    credentials 'aws_iam_role={}'
    format as json '{}' region 'us-west-2';
""").format(config.get("S3", "LOG_DATA"), config.get("IAM_ROLE", "ARN"), config.get("S3", "LOG_JSONPATH"))

staging_songs_copy = ("""
    copy staging_songs from '{}'
    credentials 'aws_iam_role={}'
    format as json 'auto' region 'us-west-2';
""").format(config.get("S3", "SONG_DATA"), config.get("IAM_ROLE", "ARN"))

# FINAL TABLES

songplay_table_insert = ("""
insert into songplays(start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
select distinct
    timestamp 'epoch' + evnt.ts/1000 * interval '1 second' as start_time,
    evnt.user_id, evnt.level, sng.song_id, sng.artist_id, evnt.session_id, evnt.location, evnt.user_agent
from staging_events evnt, staging_songs sng
where evnt.song = sng.title
and evnt.page = 'NextSong'
and user_id not in (select distinct sp.user_id from songplays sp where sp.user_id = user_id
                    and sp.session_id = session_id and sp.start_time = start_time)
""")

user_table_insert = ("""
insert into users(user_id, first_name, last_name, gender, level)
select distinct user_id, first_name, last_name, gender, level
from staging_events
where page = 'NextSong'
and user_id not in (select distinct user_id from users)
""")

song_table_insert = ("""
insert into songs(song_id, title, artist_id, year, duration)
select distinct song_id, title, artist_id, year, duration
from staging_songs
where song_id not in (select distinct song_id from songs)
""")

artist_table_insert = ("""
insert into artists(artist_id, name, location, latitude, longitude)
select distinct artist_id, artist_name, artist_location, artist_latitude, artist_longitude
from staging_songs
where artist_id not in (select distinct artist_id from artists)
""")

time_table_insert = ("""
insert into time(start_time, hour, day, week_of_year, month, year, weekday)
select distinct start_time,
    extract(hour from start_time),
    extract(day from start_time),
    extract(week from start_time),
    extract(month from start_time),
    extract(year from start_time),
    extract(dayofweek from start_time)
from (select distinct timestamp 'epoch' + ts/1000 * interval '1 second' as start_time from staging_events)
where start_time not in (select distinct start_time from time)
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
