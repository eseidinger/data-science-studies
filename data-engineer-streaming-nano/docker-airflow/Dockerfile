FROM python:3.7.5

ARG AIRFLOW_USER_HOME=/usr/local/airflow
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}

RUN useradd -ms /bin/bash -d ${AIRFLOW_USER_HOME} airflow
RUN pip install apache-airflow boto3 psycopg2 sql

COPY entrypoint.sh /entrypoint.sh
RUN chown -R airflow: ${AIRFLOW_USER_HOME}

EXPOSE 8080 5555 8793

USER airflow
WORKDIR ${AIRFLOW_USER_HOME}
ENTRYPOINT ["/entrypoint.sh"]

CMD ["webserver"]
