# kafka_example_dag_1.py 

import os
import json
import logging
import functools
from pendulum import datetime
import socket

from airflow.decorators import task
from airflow import DAG
from airflow_provider_kafka.operators.produce_to_topic import ProduceToTopicOperator
from airflow_provider_kafka.operators.consume_from_topic import ConsumeFromTopicOperator
from airflow_provider_kafka.operators.await_message import AwaitKafkaMessageOperator

my_topic = "quickstart-events" #os.environ["KAFKA_TOPIC_NAME"]

connection_config = {'bootstrap.servers': "host.docker.internal:19092",
    "security.protocol": "PLAINTEXT"}

# with Kafka server properties:
# listeners=PLAINTEXT://:9092,RMOFF_DOCKER_HACK://:19092
# advertised.listeners=PLAINTEXT://localhost:9092,RMOFF_DOCKER_HACK://host.docker.internal:19092
# listener.security.protocol.map=PLAINTEXT:PLAINTEXT,RMOFF_DOCKER_HACK:PLAINTEXT

with DAG(
    dag_id="kafka_example_dag_1",
    start_date=datetime(2022, 11, 1),
    schedule=None,
    catchup=False,
):

    @task
    def connect_http():
        import http.client
        connection = http.client.HTTPConnection('host.docker.internal', 8000, timeout=10)
        connection.request("GET", "/")
        print(connection.getresponse().status)
        return "hi"

    connect_http()

    def producer_function():
        for i in range(5):
            yield (json.dumps(i), json.dumps(i+1))

    producer_task = ProduceToTopicOperator(
        task_id=f"produce_to_{my_topic}",
        topic=my_topic,
        producer_function=producer_function, 
        kafka_config=connection_config
    )

    consumer_logger = logging.getLogger("airflow")
    def consumer_function(message, prefix=None):
        try:
            key = json.loads(message.key())
            value = json.loads(message.value())
            consumer_logger.info(f"{prefix} {message.topic()} @ {message.offset()}; {key} : {value}")
            return
        except:
            return

    consumer_task = ConsumeFromTopicOperator(
        task_id=f"consume_from_{my_topic}",
        topics=[my_topic],
        apply_function=functools.partial(consumer_function, prefix="consumed:::"),
        consumer_config={
            **connection_config,
            "group.id": "foo",
            "enable.auto.commit": False,
            "auto.offset.reset": "beginning",
        },
        max_messages=30,
        max_batch_size=10,
    )

    def await_function(message):
        if message is not None:
            if isinstance(json.loads(message.value()), int):
                if json.loads(message.value()) % 5 == 0:
                    return f" Got the following message: {json.loads(message.value())}"

    await_message = AwaitKafkaMessageOperator(
        task_id=f"awaiting_message_in_{my_topic}",
        topics=[my_topic],
        apply_function="kafka_example_dag_1.await_function", #this needs to be passed in as a module, function direct does not work!!!!
        kafka_config={
            **connection_config,
            "group.id": "awaiting_message",
            "enable.auto.commit": False,
            "auto.offset.reset": "beginning",
        },
        xcom_push_key="retrieved_message",
        poll_interval=1
    )

    producer_task >> consumer_task >> await_message