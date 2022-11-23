FROM quay.io/astronomer/astro-runtime:6.0.3

RUN pip install confluent-kafka
RUN pip install airflow-provider-kafka