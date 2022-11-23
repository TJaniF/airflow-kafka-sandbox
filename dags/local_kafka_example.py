import functools
import json
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


from airflow_provider_kafka.operators.await_message import AwaitKafkaMessageOperator
from airflow_provider_kafka.operators.consume_from_topic import ConsumeFromTopicOperator
from airflow_provider_kafka.operators.produce_to_topic import ProduceToTopicOperator


default_args = {
    "owner": "airflow",
    "depend_on_past": False,
    "start_date": datetime(2021, 7, 20),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def producer_function():
    for i in range(5):
        yield (json.dumps(i), json.dumps("produced by Airflow"))



consumer_logger = logging.getLogger("airflow")
def consumer_function(message, prefix=None):
    try:
        key = json.loads(message.key())
        value = json.loads(message.value())
        consumer_logger.info(f"{prefix} {message.topic()} @ {message.offset()}; {key} : {value}")
        return
    except:
        return

def await_function(message):
    if json.loads(message.value()) % 5 == 0:
        return f" Got the following message: {json.loads(message.value())}"

def hello_kafka():
    print("Hello Kafka !")
    return

with DAG(
    "local-kafka-example",
    default_args=default_args,
    description="Examples of Kafka Operators",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:

    

    config_kwargs = {
        "bootstrap.servers": "pkc-zpjg0.eu-central-1.aws.confluent.cloud:9092",
        }

    t3 = ProduceToTopicOperator(
        task_id="plain_producer",
        topic="test_topic_1",
        producer_function=producer_function, 
        kafka_config=config_kwargs
    )

    t4 = ConsumeFromTopicOperator(
        task_id="consume_from_topic_2",
        topics=["test_topic_1"],
        apply_function=functools.partial(consumer_function, prefix="consumed:::"),
        consumer_config={
            "bootstrap.servers": "pkc-zpjg0.eu-central-1.aws.confluent.cloud:9092",
            "group.id": "foo",
            "enable.auto.commit": False,
            "auto.offset.reset": "beginning",
        },
        max_messages=30,
        max_batch_size=10,
    )

    t4.doc_md = 'Does the same thing as the t2 task, but passes the callable directly instead of using the string notation.'

    t5 = AwaitKafkaMessageOperator(
        task_id="awaiting_message",
        topics=["test_topic_1"],
        apply_function="provider_example_code.await_function", #this needs to be passed in as a module, function direct does not work!!!!
        kafka_config={
        "bootstrap.servers": "pkc-zpjg0.eu-central-1.aws.confluent.cloud:9092",
        "group.id": "awaiting_message",
        "enable.auto.commit": False
    },
        xcom_push_key="retrieved_message",
    )

    t6 = PythonOperator(
        task_id='hello_kafka',
        python_callable=hello_kafka
    )

    t6.doc_md = 'The task that is executed after the deferable task returns for execution.'
    
    t3 >> t4 >> t5 >> t6