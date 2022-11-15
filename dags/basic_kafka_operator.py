from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from pendulum import datetime
from airflow_provider_kafka.operators.await_message import AwaitKafkaMessageOperator
from airflow.operators.bash import BashOperator
import requests


with DAG(
    dag_id="basic_kafka_operator",
    start_date=datetime(2022,11,14),
    schedule=None,
    catchup=False
):

    t1 = EmptyOperator(task_id="t1")

    @task
    def get_clusters():
        re = requests.get("GET http://localhost:8090/kafka/v3/clusters/")
        return re.json()

    get_clusters()

    t2 = BashOperator(
        task_id="t2",
        bash_command="curl -sS -o docker-compose.yml https://raw.githubusercontent.com/confluentinc/cp-all-in-one/7.3.0-post/cp-all-in-one-cloud/docker-compose.yml"
    )