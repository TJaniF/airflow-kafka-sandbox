FROM quay.io/astronomer/astro-runtime:6.0.3-base

RUN apt-get update
RUN apt install librdkafka-dev -y
ENV C_INCLUDE_PATH=/opt/homebrew/Cellar/librdkafka/1.8.2/include
ENV LIBRARY_PATH=/opt/homebrew/Cellar/librdkafka/1.8.2/lib
RUN pip install confluent-kafka
RUN pip install airflow-provider-kafka