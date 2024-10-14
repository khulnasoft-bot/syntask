# syntask-azure

<p align="center">
    <a href="https://pypi.python.org/pypi/syntask-azure/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/syntask-azure?color=26272B&labelColor=090422"></a>
    <a href="https://pepy.tech/badge/syntask-azure/" alt="Downloads">
        <img src="https://img.shields.io/pypi/dm/syntask-azure?color=26272B&labelColor=090422" /></a>
</p>

`syntask-azure` is a collection of Syntask integrations for orchestration workflows with Azure.

## Getting Started

### Installation

Install `syntask-azure` with `pip`

```bash
pip install syntask-azure
```

To use Blob Storage:

```bash
pip install "syntask-azure[blob_storage]"
```

To use Cosmos DB:

```bash
pip install "syntask-azure[cosmos_db]"
```

To use ML Datastore:

```bash
pip install "syntask-azure[ml_datastore]"
```

## Examples

### Download a blob

```python
from syntask import flow

from syntask_azure import AzureBlobStorageCredentials
from syntask_azure.blob_storage import blob_storage_download

@flow
def example_blob_storage_download_flow():
    connection_string = "connection_string"
    blob_storage_credentials = AzureBlobStorageCredentials(
        connection_string=connection_string,
    )
    data = blob_storage_download(
        blob="syntask.txt",
        container="syntask",
        azure_credentials=blob_storage_credentials,
    )
    return data

example_blob_storage_download_flow()
```

Use `with_options` to customize options on any existing task or flow:

```python
custom_blob_storage_download_flow = example_blob_storage_download_flow.with_options(
    name="My custom task name",
    retries=2,
    retry_delay_seconds=10,
)
```

### Run a command on an Azure container instance

```python
from syntask import flow
from syntask_azure import AzureContainerInstanceCredentials
from syntask_azure.container_instance import AzureContainerInstanceJob


@flow
def container_instance_job_flow():
    aci_credentials = AzureContainerInstanceCredentials.load("MY_BLOCK_NAME")
    container_instance_job = AzureContainerInstanceJob(
        aci_credentials=aci_credentials,
        resource_group_name="azure_resource_group.example.name",
        subscription_id="<MY_AZURE_SUBSCRIPTION_ID>",
        command=["echo", "hello world"],
    )
    return container_instance_job.run()
```

### Use Azure Container Instance as infrastructure

If we have `a_flow_module.py`:

```python
from syntask import flow
from syntask.logging import get_run_logger

@flow
def log_hello_flow(name="Marvin"):
    logger = get_run_logger()
    logger.info(f"{name} said hello!")

if __name__ == "__main__":
    log_hello_flow()
```

We can run that flow using an Azure Container Instance, but first create the infrastructure block:

```python
from syntask_azure import AzureContainerInstanceCredentials
from syntask_azure.container_instance import AzureContainerInstanceJob

container_instance_job = AzureContainerInstanceJob(
    aci_credentials=AzureContainerInstanceCredentials.load("MY_BLOCK_NAME"),
    resource_group_name="azure_resource_group.example.name",
    subscription_id="<MY_AZURE_SUBSCRIPTION_ID>",
)
container_instance_job.save("aci-dev")
```

Then, create the deployment either on the UI or through the CLI:

```bash
syntask deployment build a_flow_module.py:log_hello_flow --name aci-dev -ib container-instance-job/aci-dev
```

Visit [Syntask Deployments](https://docs.syntask.khulnasoft.com/latest/deploy/) for more information about deployments.

## Azure Container Instance Worker

The Azure Container Instance worker is an excellent way to run
your workflows on Azure.

To get started, create an Azure Container Instances typed work pool:

```
syntask work-pool create -t azure-container-instance my-aci-work-pool
```

Then, run a worker that pulls jobs from the work pool:

```
syntask worker start -n my-aci-worker -p my-aci-work-pool
```

The worker should automatically read the work pool's type and start an
Azure Container Instance worker.
