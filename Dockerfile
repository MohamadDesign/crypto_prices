FROM apache/airflow:2.9.1

USER airflow

RUN pip install --no-cache-dir apache-airflow-providers-apache-kafka==1.2.0
RUN pip install kafka-python

USER root
