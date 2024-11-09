---
description: Syntask blocks package configuration storage, infrastructure, and secrets for use with deployments or flow scripts.
tags:
  - blocks
  - storage
  - secrets
  - configuration
  - infrastructure
  - deployments
search:
  boost: 2
---

# Blocks

Blocks are a primitive within Syntask that enable the storage of configuration and provide an interface for interacting with external systems.

With blocks, you can securely store credentials for authenticating with services like AWS, GitHub, Slack, and any other system you'd like to orchestrate with Syntask. 

Blocks expose methods that provide pre-built functionality for performing actions against an external system. They can be used to download data from or upload data to an S3 bucket, query data from or write data to a database, or send a message to a Slack channel.

You may configure blocks through code or via the Syntask Cloud and the Syntask server UI.

You can access blocks for both configuring flow [deployments](/concepts/deployments/) and directly from within your flow code.

Syntask provides some built-in block types that you can use right out of the box. Additional blocks are available through [Syntask Integrations](/integrations/). To use these blocks you can `pip install` the package, then register the blocks you want to use with Syntask Cloud or a Syntask server.

Syntask Cloud and the Syntask server UI display a library of block types available for you to configure blocks that may be used by your flows.

![Viewing the new block library in the Syntask UI](/img/ui/block-library.png)

!!! tip "Blocks and parameters"
    Blocks are useful for configuration that needs to be shared across flow runs and between flows.

    For configuration that will change between flow runs, we recommend using [parameters](/concepts/flows/#parameters).

## Syntask built-in blocks

Syntask provides a broad range of commonly used, built-in block types. These block types are available in Syntask Cloud and the Syntask server UI.

| Block                                                                                                                | Slug                                                     | Description                                                                                                                             |
| -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| [Azure](/concepts/filesystems/#azure)                                                                                | `azure`                                                  | Store data as a file on Azure Datalake and Azure Blob Storage.                                                                          |
| [Date Time](/api-ref/syntask/blocks/system/#syntask.blocks.system.DateTime)                                          | `date-time`                                              | A block that represents a datetime.                                                                                                     |
| [Docker Container](/api-ref/syntask/infrastructure/#syntask.infrastructure.DockerContainer)                          | `docker-container`                                       | Runs a command in a container.                                                                                                          |
| [Docker Registry](/api-ref/syntask/infrastructure/#syntask.infrastructure.docker.DockerRegistry)                     | `docker-registry`                                        | Connects to a Docker registry.  Requires a Docker Engine to be connectable.                                                             |
| [GCS](/concepts/filesystems/#gcs)                                                                                    | `gcs`                                                    | Store data as a file on Google Cloud Storage.                                                                                           |
| [GitHub](/concepts/filesystems/#github)                                                                              | `github`                                                 | Interact with files stored on public GitHub repositories.                                                                               |
| [JSON](/api-ref/syntask/blocks/system/#syntask.blocks.system.JSON)                                                   | `json`                                                   | A block that represents JSON.                                                                                                           |
| [Kubernetes Cluster Config](/api-ref/syntask/blocks/kubernetes/#syntask.blocks.kubernetes.KubernetesClusterConfig)   | <span class="no-wrap">`kubernetes-cluster-config`</span> | Stores configuration for interaction with Kubernetes clusters.                                                                          |
| [Kubernetes Job](/api-ref/syntask/infrastructure/#syntask.infrastructure.KubernetesJob)                              | `kubernetes-job`                                         | Runs a command as a Kubernetes Job.                                                                                                     |
| [Local File System](/concepts/filesystems/#local-filesystem)                                                         | `local-file-system`                                      | Store data as a file on a local file system.                                                                                            |
| [Microsoft Teams Webhook](/api-ref/syntask/blocks/notifications/#syntask.blocks.notifications.MicrosoftTeamsWebhook) | `ms-teams-webhook`                                       | Enables sending notifications via a provided Microsoft Teams webhook.                                                                   |
| [Opsgenie Webhook](/api-ref/syntask/blocks/notifications/#syntask.blocks.notifications.OpsgenieWebhook)              | `opsgenie-webhook`                                       | Enables sending notifications via a provided Opsgenie webhook.                                                                          |
| [Pager Duty Webhook](/api-ref/syntask/blocks/notifications/#syntask.blocks.notifications.PagerDutyWebHook)           | `pager-duty-webhook`                                     | Enables sending notifications via a provided PagerDuty webhook.                                                                         |
| [Process](/concepts/infrastructure/#process)                                                                         | `process`                                                | Run a command in a new process.                                                                                                         |
| [Remote File System](/concepts/filesystems/#remote-file-system)                                                      | `remote-file-system`                                     | Store data as a file on a remote file system.  Supports any remote file system supported by `fsspec`.                                   |
| [S3](/concepts/filesystems/#s3)                                                                                      | `s3`                                                     | Store data as a file on AWS S3.                                                                                                         |
| [Secret](/api-ref/syntask/blocks/system/#syntask.blocks.system.Secret)                                               | `secret`                                                 | A block that represents a secret value. The value stored in this block will be obfuscated when this block is logged or shown in the UI. |
| [Slack Webhook](/api-ref/syntask/blocks/notifications/#syntask.blocks.notifications.SlackWebhook)                    | `slack-webhook`                                          | Enables sending notifications via a provided Slack webhook.                                                                             |
| [SMB](/concepts/filesystems/#smb)                                                                                    | `smb`                                                    | Store data as a file on a SMB share.                                                                                                    |
| [String](/api-ref/syntask/blocks/system/#syntask.blocks.system.String)                                               | `string`                                                 | A block that represents a string.                                                                                                       |
| [Twilio SMS](/api-ref/syntask/blocks/notifications/#syntask.blocks.notifications.TwilioSMS)                          | `twilio-sms`                                             | Enables sending notifications via Twilio SMS.                                                                                           |
| [Webhook](/api-ref/syntask/blocks/webhook/#syntask.blocks.webhook.Webhook)                                           | `webhook`                                                | Block that enables calling webhooks.                                                                                                    |

## Blocks in Syntask Integrations

Blocks can also be created by anyone and shared with the community. You'll find blocks that are available for consumption in many of the published [Syntask Integrations](/integrations/). The following table provides an overview of the blocks available from our most popular Syntask Integrations.

| Integration                                                             | Block                                                                                                                                                       | Slug                                   |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| [syntask-airbyte](https://syntaskhq.github.io/syntask-airbyte/)         | [Airbyte Connection](https://syntaskhq.github.io/syntask-airbyte/connections/#syntask_airbyte.connections.AirbyteConnection)                                | `airbyte-connection`                   |
| [syntask-airbyte](https://syntaskhq.github.io/syntask-airbyte/)         | [Airbyte Server](https://syntaskhq.github.io/syntask-airbyte/server/#syntask_airbyte.server.AirbyteServer)                                                  | `airbyte-server`                       |
| [syntask-aws](https://syntaskhq.github.io/syntask-aws/)                 | [AWS Credentials](https://syntaskhq.github.io/syntask-aws/credentials/#syntask_aws.credentials.AwsCredentials)                                              | `aws-credentials`                      |
| [syntask-aws](https://syntaskhq.github.io/syntask-aws/)                 | [ECS Task](https://syntaskhq.github.io/syntask-aws/ecs/#syntask_aws.ecs.ECSTask)                                                                            | `ecs-task`                             |
| [syntask-aws](https://syntaskhq.github.io/syntask-aws/)                 | [MinIO Credentials](https://syntaskhq.github.io/syntask-aws/credentials/#syntask_aws.credentials.MinIOCredentials)                                          | `minio-credentials`                    |
| [syntask-aws](https://syntaskhq.github.io/syntask-aws/)                 | [S3 Bucket](https://syntaskhq.github.io/syntask-aws/s3/#syntask_aws.s3.S3Bucket)                                                                            | `s3-bucket`                            |
| [syntask-azure](https://syntaskhq.github.io/syntask-azure/)             | [Azure Blob Storage Credentials](https://syntaskhq.github.io/syntask-azure/credentials/#syntask_azure.credentials.AzureBlobStorageCredentials)              | `azure-blob-storage-credentials`       |
| [syntask-azure](https://syntaskhq.github.io/syntask-azure/)             | [Azure Container Instance Credentials](https://syntaskhq.github.io/syntask-azure/credentials/#syntask_azure.credentials.AzureContainerInstanceCredentials)  | `azure-container-instance-credentials` |
| [syntask-azure](https://syntaskhq.github.io/syntask-azure/)             | [Azure Container Instance Job](https://syntaskhq.github.io/syntask-azure/container_instance/#syntask_azure.container_instance.AzureContainerInstanceJob)    | `azure-container-instance-job`         |
| [syntask-azure](https://syntaskhq.github.io/syntask-azure/)             | [Azure Cosmos DB Credentials](https://syntaskhq.github.io/syntask-azure/credentials/#syntask_azure.credentials.AzureCosmosDbCredentials)                    | `azure-cosmos-db-credentials`          |
| [syntask-azure](https://syntaskhq.github.io/syntask-azure/)             | [AzureML Credentials](https://syntaskhq.github.io/syntask-azure/credentials/#syntask_azure.credentials.AzureMlCredentials)                                  | `azureml-credentials`                  |
| [syntask-bitbucket](https://syntaskhq.github.io/syntask-bitbucket/)     | [BitBucket Credentials](https://syntaskhq.github.io/syntask-bitbucket/credentials/)                                                                         | `bitbucket-credentials`                |
| [syntask-bitbucket](https://syntaskhq.github.io/syntask-bitbucket/)     | [BitBucket Repository](https://syntaskhq.github.io/syntask-bitbucket/repository/)                                                                           | `bitbucket-repository`                 |
| [syntask-census](https://syntaskhq.github.io/syntask-census/)           | [Census Credentials](https://syntaskhq.github.io/syntask-census/credentials/)                                                                               | `census-credentials`                   |
| [syntask-census](https://syntaskhq.github.io/syntask-census/)           | [Census Sync](https://syntaskhq.github.io/syntask-census/syncs/)                                                                                            | `census-sync`                          |
| [syntask-databricks](https://syntaskhq.github.io/syntask-databricks/)   | [Databricks Credentials](https://syntaskhq.github.io/syntask-databricks/credentials/#syntask_databricks.credentials.DatabricksCredentials)                  | `databricks-credentials`               |
| [syntask-dbt](https://syntaskhq.github.io/syntask-dbt/)                 | [dbt CLI BigQuery Target Configs](https://syntaskhq.github.io/syntask-dbt/cli/configs/bigquery/#syntask_dbt.cli.configs.bigquery.BigQueryTargetConfigs)     | `dbt-cli-bigquery-target-configs`      |
| [syntask-dbt](https://syntaskhq.github.io/syntask-dbt/)                 | [dbt CLI Profile](https://syntaskhq.github.io/syntask-dbt/cli/credentials/#syntask_dbt.cli.credentials.DbtCliProfile)                                       | `dbt-cli-profile`                      |
| [syntask-dbt](https://syntaskhq.github.io/syntask-dbt/)                 | [dbt Cloud Credentials](https://syntaskhq.github.io/syntask-dbt/cloud/credentials/#syntask_dbt.cloud.credentials.DbtCloudCredentials)                       | `dbt-cloud-credentials`                |
| [syntask-dbt](https://syntaskhq.github.io/syntask-dbt/)                 | [dbt CLI Global Configs](https://syntaskhq.github.io/syntask-dbt/cli/configs/base/#syntask_dbt.cli.configs.base.GlobalConfigs)                              | `dbt-cli-global-configs`               |
| [syntask-dbt](https://syntaskhq.github.io/syntask-dbt/)                 | [dbt CLI Postgres Target Configs](https://syntaskhq.github.io/syntask-dbt/cli/configs/postgres/#syntask_dbt.cli.configs.postgres.PostgresTargetConfigs)     | `dbt-cli-postgres-target-configs`      |
| [syntask-dbt](https://syntaskhq.github.io/syntask-dbt/)                 | [dbt CLI Snowflake Target Configs](https://syntaskhq.github.io/syntask-dbt/cli/configs/snowflake/#syntask_dbt.cli.configs.snowflake.SnowflakeTargetConfigs) | `dbt-cli-snowflake-target-configs`     |
| [syntask-dbt](https://syntaskhq.github.io/syntask-dbt/)                 | [dbt CLI Target Configs](https://syntaskhq.github.io/syntask-dbt/cli/configs/base/#syntask_dbt.cli.configs.base.TargetConfigs)                              | `dbt-cli-target-configs`               |
| [syntask-docker](https://syntaskhq.github.io/syntask-docker/)           | [Docker Host](https://syntaskhq.github.io/syntask-docker/host/)                                                                                             | `docker-host`                          |
| [syntask-docker](https://syntaskhq.github.io/syntask-docker/)           | [Docker Registry Credentials](https://syntaskhq.github.io/syntask-docker/credentials/)                                                                      | `docker-registry-credentials`          |
| [syntask-email](https://syntaskhq.github.io/syntask-email/)             | [Email Server Credentials](https://syntaskhq.github.io/syntask-email/credentials/)                                                                          | `email-server-credentials`             |
| [syntask-firebolt](https://syntaskhq.github.io/syntask-firebolt/)       | [Firebolt Credentials](https://syntaskhq.github.io/syntask-firebolt/credentials/)                                                                           | `firebolt-credentials`                 |
| [syntask-firebolt](https://syntaskhq.github.io/syntask-firebolt/)       | [Firebolt Database](https://syntaskhq.github.io/syntask-firebolt/database/)                                                                                 | `firebolt-database`                    |
| [syntask-gcp](https://syntaskhq.github.io/syntask-gcp/)                 | [BigQuery Warehouse](https://syntaskhq.github.io/syntask-gcp/bigquery/#syntask_gcp.bigquery.BigQueryWarehouse)                                              | `bigquery-warehouse`                   |
| [syntask-gcp](https://syntaskhq.github.io/syntask-gcp/)                 | [GCP Cloud Run Job](https://syntaskhq.github.io/syntask-gcp/cloud_run/#syntask_gcp.cloud_run.CloudRunJob)                                                   | `cloud-run-job`                        |
| [syntask-gcp](https://syntaskhq.github.io/syntask-gcp/)                 | [GCP Credentials](https://syntaskhq.github.io/syntask-gcp/credentials/#syntask_gcp.credentials.GcpCredentials)                                              | `gcp-credentials`                      |
| [syntask-gcp](https://syntaskhq.github.io/syntask-gcp/)                 | [GcpSecret](https://syntaskhq.github.io/syntask-gcp/secret_manager/#syntask_gcp.secret_manager.GcpSecret)                                                   | `gcpsecret`                            |
| [syntask-gcp](https://syntaskhq.github.io/syntask-gcp/)                 | [GCS Bucket](https://syntaskhq.github.io/syntask-gcp/cloud_storage/#syntask_gcp.cloud_storage.GcsBucket)                                                    | `gcs-bucket`                           |
| [syntask-gcp](https://syntaskhq.github.io/syntask-gcp/)                 | [Vertex AI Custom Training Job](https://syntaskhq.github.io/syntask-gcp/aiplatform/#syntask_gcp.aiplatform.VertexAICustomTrainingJob)                       | `vertex-ai-custom-training-job`        |
| [syntask-github](https://syntaskhq.github.io/syntask-github/)           | [GitHub Credentials](https://syntaskhq.github.io/syntask-github/credentials/)                                                                               | `github-credentials`                   |
| [syntask-github](https://syntaskhq.github.io/syntask-github/)           | [GitHub Repository](https://syntaskhq.github.io/syntask-github/repository/)                                                                                 | `github-repository`                    |
| [syntask-gitlab](https://syntaskhq.github.io/syntask-gitlab/)           | [GitLab Credentials](https://syntaskhq.github.io/syntask-gitlab/credentials/)                                                                               | `gitlab-credentials`                   |
| [syntask-gitlab](https://syntaskhq.github.io/syntask-gitlab/)           | [GitLab Repository](https://syntaskhq.github.io/syntask-gitlab/repositories/)                                                                               | `gitlab-repository`                    |
| [syntask-hex](https://syntaskhq.github.io/syntask-hex/)                 | [Hex Credentials](https://syntaskhq.github.io/syntask-hex/credentials/#syntask_hex.credentials.HexCredentials)                                              | `hex-credentials`                      |
| [syntask-hightouch](https://syntaskhq.github.io/syntask-hightouch/)     | [Hightouch Credentials](https://syntaskhq.github.io/syntask-hightouch/credentials/)                                                                         | `hightouch-credentials`                |
| [syntask-kubernetes](https://syntaskhq.github.io/syntask-kubernetes/)   | [Kubernetes Credentials](https://syntaskhq.github.io/syntask-kubernetes/credentials/)                                                                       | `kubernetes-credentials`               |
| [syntask-monday](https://syntaskhq.github.io/syntask-monday/)           | [Monday Credentials](https://syntaskhq.github.io/syntask-monday/credentials/)                                                                               | `monday-credentials`                   |
| [syntask-monte-carlo](https://syntaskhq.github.io/syntask-monte-carlo/) | [Monte Carlo Credentials](https://syntaskhq.github.io/syntask-monte-carlo/credentials/)                                                                     | `monte-carlo-credentials`              |
| [syntask-openai](https://syntaskhq.github.io/syntask-openai/)           | [OpenAI Completion Model](https://syntaskhq.github.io/syntask-openai/completion/#syntask_openai.completion.CompletionModel)                                 | `openai-completion-model`              |
| [syntask-openai](https://syntaskhq.github.io/syntask-openai/)           | [OpenAI Image Model](https://syntaskhq.github.io/syntask-openai/image/#syntask_openai.image.ImageModel)                                                     | `openai-image-model`                   |
| [syntask-openai](https://syntaskhq.github.io/syntask-openai/)           | [OpenAI Credentials](https://syntaskhq.github.io/syntask-openai/credentials/#syntask_openai.credentials.OpenAICredentials)                                  | `openai-credentials`                   |
| [syntask-slack](https://syntaskhq.github.io/syntask-slack/)             | [Slack Credentials](https://syntaskhq.github.io/syntask-slack/credentials/#syntask_slack.credentials.SlackCredentials)                                      | `slack-credentials`                    |
| [syntask-slack](https://syntaskhq.github.io/syntask-slack/)             | [Slack Incoming Webhook](https://syntaskhq.github.io/syntask-slack/credentials/#syntask_slack.credentials.SlackWebhook)                                     | `slack-incoming-webhook`               |
| [syntask-snowflake](https://syntaskhq.github.io/syntask-snowflake/)     | [Snowflake Connector](https://syntaskhq.github.io/syntask-snowflake/database/#syntask_snowflake.database.SnowflakeConnector)                                | `snowflake-connector`                  |
| [syntask-snowflake](https://syntaskhq.github.io/syntask-snowflake/)     | [Snowflake Credentials](https://syntaskhq.github.io/syntask-snowflake/credentials/#syntask_snowflake.credentials.SnowflakeCredentials)                      | `snowflake-credentials`                |
| [syntask-sqlalchemy](https://syntaskhq.github.io/syntask-sqlalchemy/)   | [Database Credentials](https://syntaskhq.github.io/syntask-sqlalchemy/credentials/#syntask_sqlalchemy.credentials.DatabaseCredentials)                      | `database-credentials`                 |
| [syntask-sqlalchemy](https://syntaskhq.github.io/syntask-sqlalchemy/)   | [SQLAlchemy Connector](https://syntaskhq.github.io/syntask-sqlalchemy/database/#syntask_sqlalchemy.database.SqlAlchemyConnector)                            | `sqlalchemy-connector`                 |
| [syntask-twitter](https://syntaskhq.github.io/syntask-twitter/)         | [Twitter Credentials](https://syntaskhq.github.io/syntask-twitter/credentials/)                                                                             | `twitter-credentials`                  |

## Using existing block types

Blocks are classes that subclass the `Block` base class. They can be instantiated and used like normal classes.

### Instantiating blocks

For example, to instantiate a block that stores a JSON value, use the `JSON` block:

```python
from syntask.blocks.system import JSON

json_block = JSON(value={"the_answer": 42})
```

### Saving blocks

If this JSON value needs to be retrieved later to be used within a flow or task, we can use the `.save()` method on the block to store the value in a block document on the Syntask database for retrieval later:

```python
json_block.save(name="life-the-universe-everything")
```

If you'd like to update the block value stored for a given `name`, you can overwrite the existing block document by setting `overwrite=True`:

```python
json_block.save(overwrite=True)
```

!!! Tip
    in the above example, the name `"life-the-universe-everything"` is inferred from the existing block document

... or save the same block value as a new block document by setting the `name` parameter to a new value:

```python
json_block.save(name="actually-life-the-universe-everything")
```

!!! tip "Utilizing the UI"
    Blocks documents can also be created and updated via the [Syntask UI](/ui/blocks/).

### Loading blocks

The name given when saving the value stored in the JSON block can be used when retrieving the value during a flow or task run:

```python hl_lines="6"
from syntask import flow
from syntask.blocks.system import JSON

@flow
def what_is_the_answer():
    json_block = JSON.load("life-the-universe-everything")
    print(json_block.value["the_answer"])

what_is_the_answer() # 42
```

Blocks can also be loaded with a unique slug that is a combination of a block type slug and a block document name.

To load our JSON block document from before, we can run the following:

```python hl_lines="3"
from syntask.blocks.core import Block

json_block = Block.load("json/life-the-universe-everything")
print(json_block.value["the-answer"]) #42
```

!!! tip "Sharing Blocks"
    Blocks can also be loaded by fellow Workspace Collaborators, available on [Syntask Cloud](/ui/cloud/).

### Deleting blocks

You can delete a block by using the `.delete()` method on the block:

```python
from syntask.blocks.core import Block
Block.delete("json/life-the-universe-everything")
```

You can also use the CLI to delete specific blocks with a given slug or id:

```bash
syntask block delete json/life-the-universe-everything
```

```bash
syntask block delete --id <my-id>
```


## Creating new block types

To create a custom block type, define a class that subclasses `Block`. The `Block` base class builds off of Pydantic's `BaseModel`, so custom blocks can be [declared in same manner as a Pydantic model](https://pydantic-docs.helpmanual.io/usage/models/#basic-model-usage).

Here's a block that represents a cube and holds information about the length of each edge in inches:

```python
from syntask.blocks.core import Block

class Cube(Block):
    edge_length_inches: float
```

You can also include methods on a block include useful functionality. Here's the same cube block with methods to calculate the volume and surface area of the cube:

```python hl_lines="6-10"
from syntask.blocks.core import Block

class Cube(Block):
    edge_length_inches: float

    def get_volume(self):
        return self.edge_length_inches**3

    def get_surface_area(self):
        return 6 * self.edge_length_inches**2
```

Now the `Cube` block can be used to store different cube configuration that can later be used in a flow:

```python
from syntask import flow

rubiks_cube = Cube(edge_length_inches=2.25)
rubiks_cube.save("rubiks-cube")

@flow
def calculate_cube_surface_area(cube_name):
    cube = Cube.load(cube_name)
    print(cube.get_surface_area())

calculate_cube_surface_area("rubiks-cube") # 30.375
```

### Secret fields

All block values are encrypted before being stored, but if you have values that you would not like visible in the UI or in logs, then you can use the `SecretStr` field type provided by Pydantic to automatically obfuscate those values. This can be useful for fields that are used to store credentials like passwords and API tokens.

Here's an example of an `AWSCredentials` block that uses `SecretStr`:

```python hl_lines="8"
from typing import Optional

from syntask.blocks.core import Block
from pydantic import SecretStr  # if pydantic version >= 2.0, use: from pydantic.v1 import SecretStr

class AWSCredentials(Block):
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[SecretStr] = None
    aws_session_token: Optional[str] = None
    profile_name: Optional[str] = None
    region_name: Optional[str] = None
```

Because `aws_secret_access_key` has the `SecretStr` type hint assigned to it, the value of that field will not be exposed if the object is logged:

```python
aws_credentials_block = AWSCredentials(
    aws_access_key_id="AKIAJKLJKLJKLJKLJKLJK",
    aws_secret_access_key="secret_access_key"
)

print(aws_credentials_block)
# aws_access_key_id='AKIAJKLJKLJKLJKLJKLJK' aws_secret_access_key=SecretStr('**********') aws_session_token=None profile_name=None region_name=None
```

There's  also use the `SecretDict` field type provided by Syntask. This type will allow you to add a dictionary field to your block that will have values at all levels automatically obfuscated in the UI or in logs. This is useful for blocks where typing or structure of secret fields is not known until configuration time.

Here's an example of a block that uses `SecretDict`:

```python
from typing import Dict

from syntask.blocks.core import Block
from syntask.blocks.fields import SecretDict


class SystemConfiguration(Block):
    system_secrets: SecretDict
    system_variables: Dict


system_configuration_block = SystemConfiguration(
    system_secrets={
        "password": "p@ssw0rd",
        "api_token": "token_123456789",
        "private_key": "<private key here>",
    },
    system_variables={
        "self_destruct_countdown_seconds": 60,
        "self_destruct_countdown_stop_time": 7,
    },
)
```
`system_secrets` will be obfuscated when `system_configuration_block` is displayed, but `system_variables` will be shown in plain-text:

```python
print(system_configuration_block)
# SystemConfiguration(
#   system_secrets=SecretDict('{'password': '**********', 'api_token': '**********', 'private_key': '**********'}'), 
#   system_variables={'self_destruct_countdown_seconds': 60, 'self_destruct_countdown_stop_time': 7}
# )
```
### Blocks metadata

The way that a block is displayed can be controlled by metadata fields that can be set on a block subclass.

Available metadata fields include:

| Property          | Description                                                                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| \_block_type_name | Display name of the block in the UI. Defaults to the class name.                                                                             |
| \_block_type_slug | Unique slug used to reference the block type in the API. Defaults to a lowercase, dash-delimited version of the block type name.             |
| \_logo_url        | URL pointing to an image that should be displayed for the block type in the UI. Default to `None`.                                           |
| \_description     | Short description of block type. Defaults to docstring, if provided.                                                                         |
| \_code_example    | Short code snippet shown in UI for how to load/use block type. Default to first example provided in the docstring of the class, if provided. |

### Nested blocks

Block are composable. This means that you can create a block that uses functionality from another block by declaring it as an attribute on the block that you're creating. It also means that configuration can be changed for each block independently, which allows configuration that may change on different time frames to be easily managed and configuration can be shared across multiple use cases.

To illustrate, here's a an expanded `AWSCredentials` block that includes the ability to get an authenticated session via the `boto3` library:

```python
from typing import Optional

import boto3
from syntask.blocks.core import Block
from pydantic import SecretStr

class AWSCredentials(Block):
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[SecretStr] = None
    aws_session_token: Optional[str] = None
    profile_name: Optional[str] = None
    region_name: Optional[str] = None

    def get_boto3_session(self):
        return boto3.Session(
            aws_access_key_id = self.aws_access_key_id
            aws_secret_access_key = self.aws_secret_access_key
            aws_session_token = self.aws_session_token
            profile_name = self.profile_name
            region_name = self.region
        )
```

The `AWSCredentials` block can be used within an S3Bucket block to provide authentication when interacting with an S3 bucket:

```python hl_lines="5"
import io

class S3Bucket(Block):
    bucket_name: str
    credentials: AWSCredentials

    def read(self, key: str) -> bytes:
        s3_client = self.credentials.get_boto3_session().client("s3")

        stream = io.BytesIO()
        s3_client.download_fileobj(Bucket=self.bucket_name, key=key, Fileobj=stream)

        stream.seek(0)
        output = stream.read()

        return output

    def write(self, key: str, data: bytes) -> None:
        s3_client = self.credentials.get_boto3_session().client("s3")
        stream = io.BytesIO(data)
        s3_client.upload_fileobj(stream, Bucket=self.bucket_name, Key=key)
```

You can use this `S3Bucket` block with previously saved `AWSCredentials` block values in order to interact with the configured S3 bucket:

```python
my_s3_bucket = S3Bucket(
    bucket_name="my_s3_bucket",
    credentials=AWSCredentials.load("my_aws_credentials")
)

my_s3_bucket.save("my_s3_bucket")
```

Saving block values like this links the values of the two blocks so that any changes to the values stored for the `AWSCredentials` block with the name `my_aws_credentials` will be seen the next time that block values for the `S3Bucket` block named `my_s3_bucket` is loaded.

Values for nested blocks can also be hard coded by not first saving child blocks:

```python
my_s3_bucket = S3Bucket(
    bucket_name="my_s3_bucket",
    credentials=AWSCredentials(
        aws_access_key_id="AKIAJKLJKLJKLJKLJKLJK",
        aws_secret_access_key="secret_access_key"
    )
)

my_s3_bucket.save("my_s3_bucket")
```

In the above example, the values for `AWSCredentials` are saved with `my_s3_bucket` and will not be usable with any other blocks.

### Handling updates to custom `Block` types
Let's say that you now want to add a `bucket_folder` field to your custom `S3Bucket` block that represents the default path to read and write objects from (this field exists on [our implementation](https://github.com/Synopkg/syntask-aws/blob/main/syntask_aws/s3.py#L292)).

We can add the new field to the class definition:


```python hl_lines="4"
class S3Bucket(Block):
    bucket_name: str
    credentials: AWSCredentials
    bucket_folder: str = None
    ...
```

Then [register the updated block type](#registering-blocks-for-use-in-the-syntask-ui) with either Syntask Cloud or your self-hosted Syntask server.


If you have any existing blocks of this type that were created before the update and you'd prefer to not re-create them, you can migrate them to the new version of your block type by adding the missing values:

```python
# Bypass Pydantic validation to allow your local Block class to load the old block version
my_s3_bucket_block = S3Bucket.load("my-s3-bucket", validate=False)

# Set the new field to an appropriate value
my_s3_bucket_block.bucket_path = "my-default-bucket-path"

# Overwrite the old block values and update the expected fields on the block
my_s3_bucket_block.save("my-s3-bucket", overwrite=True)
```

## Registering blocks for use in the Syntask UI

Blocks can be registered from a Python module available in the current virtual environment with a CLI command like this:

<div class="terminal">
```bash
syntask block register --module syntask_aws.credentials
```
</div>

This command is useful for registering all blocks found in the credentials module within [Syntask Integrations](/integrations/).

Or, if a block has been created in a `.py` file, the block can also be registered with the CLI command:

<div class="terminal">
```bash
syntask block register --file my_block.py
```
</div>

The registered block will then be available in the [Syntask UI](/ui/blocks/) for configuration.
