from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from pendulum import datetime


with DAG(
    dag_id="basic_kafka_operator",
    start_date=datetime(2022,11,14),
    schedule=None,
    catchup=False
):

    t1 = EmptyOperator(task_id="t1")