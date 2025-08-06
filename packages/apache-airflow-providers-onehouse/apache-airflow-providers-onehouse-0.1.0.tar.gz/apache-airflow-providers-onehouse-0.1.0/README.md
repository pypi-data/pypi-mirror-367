# Apache Airflow Provider for Onehouse

This is the Apache Airflow provider for Onehouse. It provides operators and sensors for managing Onehouse resources through Apache Airflow.

## Features

- Create and manage Onehouse clusters
- Create and run Onehouse jobs
- Monitor job and cluster status

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
   - Connection Type: `HTTP`
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
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow_providers_onehouse.operators.clusters import (
    OnehouseCreateClusterOperator,
    OnehouseDeleteClusterOperator
)
from airflow_providers_onehouse.operators.jobs import (
    OnehouseCreateJobOperator,
    OnehouseRunJobOperator
)
from airflow_providers_onehouse.sensors.onehouse import (
    OnehouseJobRunSensor,
    OnehouseCreateClusterSensor
)

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1)
}

with DAG('example_onehouse_workflow',
         default_args=default_args,
         schedule_interval=None) as dag:

    create_cluster = OnehouseCreateClusterOperator(
        task_id='create_cluster',
        cluster_config={...}  # Your cluster configuration
    )

    wait_for_cluster = OnehouseCreateClusterSensor(
        task_id='wait_for_cluster',
        request_id=create_cluster.output
    )

    create_job = OnehouseCreateJobOperator(
        task_id='create_job',
        job_config={...}  # Your job configuration
    )

    run_job = OnehouseRunJobOperator(
        task_id='run_job',
        job_name="{{ task_instance.xcom_pull(task_ids='create_job') }}"
    )

    wait_for_job = OnehouseJobRunSensor(
        task_id='wait_for_job',
        request_id=run_job.output
    )

    delete_cluster = OnehouseDeleteClusterOperator(
        task_id='delete_cluster',
        cluster_name='your-cluster-name'
    )

    create_cluster >> wait_for_cluster >> create_job >> run_job >> wait_for_job >> delete_cluster
```

## Available Operators

### Cluster Operators
- `OnehouseCreateClusterOperator`: Creates a new Onehouse cluster
- `OnehouseDeleteClusterOperator`: Deletes an existing Onehouse cluster

### Job Operators
- `OnehouseCreateJobOperator`: Creates a new Onehouse job
- `OnehouseRunJobOperator`: Runs an existing Onehouse job

### Sensors
- `OnehouseJobRunSensor`: Monitors the status of a job run
- `OnehouseCreateClusterSensor`: Monitors the status of cluster creation

## Development
### Setting up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/onehouseinc/airflow-providers-onehouse.git
   cd airflow-providers-onehouse
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. If you are creating new components like Operators, Sensors or a Hook, you need to 
    * Add the classes to the appropriate module (e.g., `operators/jobs.py`)
    * Update the module's `__init__.py` (e.g. `operators/__init__.py`) to export the class
    * Add the operator to the main `__init__.py`  (e.g. `./__init__.py`)in two places:
        * In the `operator-class-names` list in `get_provider_info()`
        * In the `__all__` list

### Running Tests
#### Unit Tests
```bash
pytest tests/unit
```
#### Integration Tests
**Setup the environment variables**
```
export AIRFLOW_CONN_ONEHOUSE_DEFAULT='{"conn_type": "onehouse", "host": "https://api.onehouse.ai", "extra": {"project_uid": "abcd", "user_id": "efgh", "api_key": "jklm", "api_secret": "opqr", "link_uid": "stuv", "region": "qxyz"}}'
```
**Run all tests**
```bash
pytest tests/integration/test_integration.py -v
```
**Run select test**
```bash
pytest tests/integration/test_integration.py::TestOnehouseIntegration::test_open_engines_clusters -v
```


### Local Testing with Docker
#### Pre-requisite:
* Install Docker

#### Steps
1. Start the Airflow environment:
   ```bash
   cd tests/integration
   docker-compose up -d
   ```

2. Access the Airflow UI at http://localhost:8080

3. Use below credentials to login
    * Username: `admin`
    * Password: `admin`

4. Stop the Airflow environment:
   ```bash
   docker-compose down -v
   ```
