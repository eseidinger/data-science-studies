echo postgres:5432:*:postgres:postgres > ~/.pgpass
chmod 0600 ~/.pgpass
createdb classroom -h postgres -U postgres > startup/startup.log 2>&1
psql -h postgres -U postgres -d classroom -c "DROP TABLE IF EXISTS purchases; CREATE TABLE purchases(id INT PRIMARY KEY, username VARCHAR(100), currency VARCHAR(10), amount INT);" > startup/startup.log 2>&1
psql -h postgres -U postgres -d classroom -c "DROP TABLE IF EXISTS clicks; CREATE TABLE clicks(id INT PRIMARY KEY, email VARCHAR(100), timestamp VARCHAR(100), uri VARCHAR(512), number INT);" > startup/startup.log 2>&1
psql -h postgres -U postgres -d classroom -c "DROP TABLE IF EXISTS connect_purchases; CREATE TABLE connect_purchases(id INT PRIMARY KEY, username VARCHAR(100), currency VARCHAR(10), amount INT);" > startup/startup.log 2>&1
psql -h postgres -U postgres -d classroom -c "DROP TABLE IF EXISTS connect_clicks; CREATE TABLE connect_clicks(id INT PRIMARY KEY, email VARCHAR(100), timestamp VARCHAR(100), uri VARCHAR(512), number INT);" > startup/startup.log 2>&1
psql -h postgres -U postgres -d classroom -c "COPY purchases(id,username,currency,amount)  FROM '/home/jovyan/work/6_kafka_intro/startup/purchases.csv' DELIMITER ',' CSV HEADER;" > startup/startup.log 2>&1
psql -h postgres -U postgres -d classroom -c "COPY clicks(id,email,timestamp,uri,number)  FROM '/home/jovyan/work/6_kafka_intro/startup/clicks.csv' DELIMITER ',' CSV HEADER;" > startup/startup.log 2>&1

createuser cta_admin -s -h postgres -U postgres > startup/startup.log 2>&1
createdb -h postgres -U postgres cta > startup/startup.log 2>&1
psql -h postgres -U postgres -d cta -c "ALTER USER cta_admin WITH PASSWORD 'chicago'" > startup/startup.log 2>&1
psql -h postgres -U postgres -d cta -c "CREATE TABLE stations (stop_id INTEGER PRIMARY KEY, direction_id VARCHAR(1) NOT NULL, stop_name VARCHAR(70) NOT NULL, station_name VARCHAR(70) NOT NULL, station_descriptive_name VARCHAR(200) NOT NULL, station_id INTEGER NOT NULL, \"order\" INTEGER, red BOOLEAN NOT NULL, blue BOOLEAN NOT NULL, green BOOLEAN NOT NULL);" > startup/startup.log 2>&1

psql -h postgres -U postgres -d cta -c "COPY stations(stop_id, direction_id,stop_name,station_name,station_descriptive_name,station_id,\"order\",red,blue,green) FROM '/home/jovyan/work/6_kafka_intro/startup/cta_stations.csv' DELIMITER ',' CSV HEADER;" > startup/startup.log 2>&1

# Configure lesson 6 and 7 streams
kafka-topics --delete --zookeeper zookeeper:2181 --topic com.udacity.streams.users > startup/startup.log 2>&1
kafka-topics --delete --zookeeper zookeeper:2181 --topic com.udacity.streams.purchases > startup/startup.log 2>&1
kafka-topics --create --zookeeper zookeeper:2181 --topic com.udacity.streams.users --replication-factor 1 --partitions 10 > startup/startup.log 2>&1
kafka-topics --create --zookeeper zookeeper:2181 --topic com.udacity.streams.purchases --replication-factor 1 --partitions 10 > startup/startup.log 2>&1
kafka-topics --delete --zookeeper zookeeper:2181 --topic com.udacity.streams.pages > startup/startup.log 2>&1
kafka-topics --delete --zookeeper zookeeper:2181 --topic com.udacity.streams.clickevents > startup/startup.log 2>&1
kafka-topics --create --zookeeper zookeeper:2181 --topic com.udacity.streams.pages --replication-factor 1 --partitions 10 > startup/startup.log 2>&1
kafka-topics --create --zookeeper zookeeper:2181 --topic com.udacity.streams.clickevents --replication-factor 1 --partitions 10 > startup/startup.log 2>&1

(python ./startup/stream.py &) &
(python ./startup/clicks.py &) &
