# Apache Airflow Provider for Onehouse

This is the Apache Airflow provider for Onehouse. It provides operators and sensors for managing Onehouse resources through Apache Airflow.

## Requirements

- Apache Airflow >= 2.9.2
- Python >= 3.10

## Installation

You can install this provider package via pip:

```bash
pip install apache-airflow-providers-onehouse
```

## Configuration

1. Set up an Airflow connection with the following details:

   - Connection Id: `onehouse_default` (or your custom connection id)
   - Connection Type: `Generic`
   - Host: `https://api.onehouse.ai`
   - Extra: Configure the following JSON:
     ```json
     {
       "project_uid": "your-project-uid",
       "user_id": "your-user-id",
       "api_key": "your-api-key",
       "api_secret": "your-api-secret",
       "link_uid": "your-link-uid",
       "region": "your-region"
     }
     ```

## Usage

### Basic Example DAG

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow_providers_onehouse.operators.jobs import (
    OnehouseCreateJobOperator,
    OnehouseRunJobOperator,
    OnehouseDeleteJobOperator,
)
from airflow_providers_onehouse.sensors.onehouse import OnehouseJobRunSensor

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

cluster_name = "cluster_1"
job_name = "job_1"

bucket_name = "bucket-name"

with DAG(
        dag_id="example_dag",
        default_args=default_args,
        description="Example DAG",
        schedule_interval=None,
        start_date=datetime(2025, 4, 28),
        catchup=False,
        tags=["onehouse", "example", "dag"],
) as dag:

    create_onehouse_job = OnehouseCreateJobOperator(
        task_id="create_onehouse_job",
        job_name=job_name,
        job_type="PYTHON",
        parameters=[
            "--conf", f"spark.archives=s3a://{bucket_name}/path/to/venv.tar.gz#environment",
            "--conf", "spark.pyspark.python=./environment/bin/python",
            f"s3a://{bucket_name}/path/to/hello_world_job.py",
        ],
        cluster_name="{{ ti.xcom_pull(task_ids='create_onehouse_cluster') }}",
        conn_id="onehouse_default",
    )

    run_onehouse_job = OnehouseRunJobOperator(
        task_id="run_onehouse_job",
        job_name="{{ ti.xcom_pull(task_ids='create_onehouse_job') }}",
        conn_id="onehouse_default",
    )

    wait_for_job = OnehouseJobRunSensor(
        task_id="wait_for_job_completion",
        job_name="{{ ti.xcom_pull(task_ids='create_onehouse_job') }}",
        job_run_id="{{ ti.xcom_pull(task_ids='run_onehouse_job') }}",
        conn_id="onehouse_default",
        poke_interval=30,
        timeout=60 * 60,
    )

    delete_onehouse_job = OnehouseDeleteJobOperator(
        task_id="delete_onehouse_job",
        job_name="{{ ti.xcom_pull(task_ids='create_onehouse_job') }}",
        conn_id="onehouse_default",
    )

    (
            create_onehouse_job
            >> run_onehouse_job
            >> wait_for_job
            >> delete_onehouse_job
    ) 
```
