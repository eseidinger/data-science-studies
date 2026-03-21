ARG BASE_CONTAINER=jupyter/all-spark-notebook
FROM $BASE_CONTAINER

LABEL maintainer="Emanuel Seidinger <dev@eseidinger.de>"

USER root

RUN apt-get update &&  apt-get -y install curl postgresql-client python-dev librocksdb-dev
# RUN curl -SL https://downloads.apache.org/kafka/2.4.0/kafka_2.12-2.4.0.tgz | tar -xzC /opt
RUN curl -SL https://packages.confluent.io/archive/5.4/confluent-community-5.4.0-2.12.tar.gz | tar -xzC /opt
# ENV PATH /opt/kafka_2.12-2.4.0/bin:$PATH
ENV PATH /opt/confluent-5.4.0/bin:$PATH
RUN conda install -c conda-forge psycopg2 cassandra-driver python-confluent-kafka python-avro fastavro faker
RUN conda install -c jetbrains kotlin-jupyter-kernel
RUN pip install "faust[rocksdb]"

USER $NB_UID
