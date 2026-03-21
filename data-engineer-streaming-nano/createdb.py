import psycopg2

conn = psycopg2.connect("host=127.0.0.1 dbname=postgres user=postgres password=postgres")
conn.set_session(autocommit=True)
cur = conn.cursor()

cur.execute("DROP DATABASE IF EXISTS studentdb")
cur.execute("DROP ROLE IF EXISTS student")
cur.execute("CREATE ROLE student WITH LOGIN PASSWORD 'student' CREATEDB")
cur.execute("CREATE DATABASE studentdb WITH ENCODING 'utf8' TEMPLATE template0")
cur.execute("GRANT ALL ON DATABASE studentdb TO student")
