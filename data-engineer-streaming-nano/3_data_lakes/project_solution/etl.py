import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format
from pyspark.sql.types import IntegerType, TimestampType
from pyspark.sql.functions import monotonically_increasing_id


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID'] = config['AWS']['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY'] = config['AWS']['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    """
    Create a spark session with hadoop-aws support.
    """
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    """
    Process song data. Extract songs and artists table from song json files.
    """
    # get filepath to song data file
    song_data = input_data + "song-data/A/A/A/*.json"
    
    # read song data file
    song_df = spark.read.json(song_data)

    # extract columns to create songs table
    songs_table = song_df.select("song_id", "title", "artist_id", "year", "duration")
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.partitionBy("year", "artist_id").parquet(output_data + "songs_out/")

    # extract columns to create artists table
    artists_table = song_df.select("artist_id", "artist_name", "artist_location", "artist_latitude", "artist_longitude") \
        .withColumnRenamed("artist_name", "name") \
        .withColumnRenamed("artist_location", "location") \
        .withColumnRenamed("artist_latitude", "latitude") \
        .withColumnRenamed("artist_longitude", "longitude")
    
    # write artists table to parquet files
    artists_table.write.parquet(output_data + "artists_out/")


def process_log_data(spark, input_data, output_data):
    """
    Process log data. Extract songplay events from JSON log files. Join with song data to get artist and song ids.
    Evaluate timestamps. Perform cleaning: remove duplicates users, remove entries without artists or song
    """
    # get filepath to log data file
    log_data = input_data + "log-data/2018/11/*.json"

    # read log data file
    log_df = spark.read.json(log_data)
    
    # filter by actions for song plays
    log_df = log_df.filter(log_df.page == "NextSong")

    # extract columns for users table    
    users_table = log_df.select("userId", "firstName", "lastName", "gender", "level") \
        .dropDuplicates() \
        .withColumnRenamed("userId", "user_id") \
        .withColumnRenamed("firstName", "first_name") \
        .withColumnRenamed("lastName", "last_name")
    
    # write users table to parquet files
    users_table.write.parquet(output_data + "users_out")

    # create timestamp column from original timestamp column
    get_timestamp = udf(lambda x: int(int(x) / 1000), IntegerType())
    log_df = log_df.withColumn("timestamp", get_timestamp(col("ts")))
    
    # create datetime column from original timestamp column
    get_datetime = udf(lambda x: datetime.fromtimestamp(x / 1000), TimestampType())
    log_df = log_df.withColumn("datetime", get_datetime(col("ts")))
    
    # extract columns to create time table
    time_table = log_df.select("datetime") \
        .withColumnRenamed("datetime", "start_time") \
        .withColumn("hour", hour("start_time")) \
        .withColumn("day", dayofmonth("start_time")) \
        .withColumn("week", weekofyear("start_time")) \
        .withColumn("month", month("start_time")) \
        .withColumn("year", year("start_time")) \
        .withColumn("weekday", date_format("start_time", "EEE"))
    
    # write time table to parquet files partitioned by year and month
    time_table.write.partitionBy("year", "month").parquet(output_data + "time_out/")

    # read in song data to use for songplays table
    song_data = input_data + "song-data/A/A/A/*.json"
    song_df = spark.read.json(song_data)

    song_df_valid = song_df.dropna(how="any", subset=["artist_name", "title"])
    log_df_valid = log_df.dropna(how="any", subset=["artist", "song"])

    # extract columns from joined song and log datasets to create songplays table 
    songplays_table = log_df_valid.join(song_df, \
                                        [log_df_valid.artist == song_df_valid.artist_name,
                                         log_df_valid.song == song_df_valid.title,
                                         log_df_valid.length == song_df_valid.duration]) \
        .select("datetime", "userId", "level", "song_id", "artist_id", "sessionId", "userAgent") \
        .withColumn("songplay_id", monotonically_increasing_id()) \
        .withColumn("year", year("datetime")) \
        .withColumn("month", month("datetime")) \
        .withColumnRenamed("datetime", "start_time") \
        .withColumnRenamed("userId", "user_id") \
        .withColumnRenamed("sessionId", "session_id") \
        .withColumnRenamed("userAgent", "user_agent")
    
    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.partitionBy("year", "month").parquet(output_data + "songplays_out/")


def main():
    """
    Configure data sources and sinks. Process song and log data.
    """
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    # input_data = "data/"
    output_data = "s3a://eseidinger-dend-p4/"
    # output_data = "output/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
