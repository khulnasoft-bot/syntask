---
description: Upgrade from Agents to Workers
tags:
    - worker
    - agent
    - deployments
    - infrastructure
    - work pool
search:
  boost: 2
---
# Upgrade from Agents to Workers

Upgrading from agents to workers significantly enhances the experience of deploying flows. It simplifies the specification of each flow's infrastructure and runtime environment.

A [worker](/concepts/work-pools/#worker-overview) is the fusion of an [agent](/concepts/agents/) with an [infrastructure block](/concepts/infrastructure/). Like agents, workers poll a work pool for flow runs that are scheduled to start. Like infrastructure blocks, workers are typed - they work with only one kind of infrastructure, and they specify the default configuration for jobs submitted to that infrastructure.

Accordingly, workers are not a drop-in replacement for agents. **Using workers requires deploying flows differently.** In particular, deploying a flow with a worker does not involve specifying an infrastructure block. Instead, infrastructure configuration is specified on the [work pool](/concepts/work-pools/) and passed to each worker that polls work from that pool.

This guide provides an overview of the differences between agents and workers. It also describes how to upgrade from agents to workers in just a few quick steps.

## Enhancements

### Workers

- Improved visibility into the status of each worker, including when a worker was started and when it last polled.
- Better handling of race conditions for high availability use cases.

### Work pools

- Work pools allow greater customization and governance of infrastructure parameters for deployments via their [base job template](/concepts/work-pools/#base-job-template).
- Syntask Cloud [push work pools](/guides/deployment/push-work-pools/) enable flow execution in your cloud provider environment without needing to host a worker.
- Syntask Cloud [managed work pools](/guides/managed-execution/) allow you to run flows on Syntask's infrastructure, without needing to host a worker or configure cloud provider infrastructure.

### Improved deployment interfaces

- The Python deployment experience with `.deploy()` or the alternative deployment experience with `syntask.yaml` are more flexible and easier to use than block and agent-based deployments.
- Both options allow you to [deploy multiple flows](/concepts/deployments/#working-with-multiple-deployments) with a single command.
- Both options allow you to build Docker images for your flows to create portable execution environments.
- The YAML-based API supports [templating](/concepts/deployments/#templating-options) to enable [dryer deployment definitions](/concepts/deployments/#reusing-configuration-across-deployments).

----------

## What's different

1. **Deployment CLI and Python SDK:**

    `syntask deployment build <entrypoint>`/`syntask deployment apply` --> [`syntask deploy`](/concepts/deployments/#deployment-declaration-reference)

    Syntask will now automatically detect flows in your repo and provide a [wizard](/#step-5-deploy-the-flow) 🧙 to guide you through setting required attributes for your deployments.

    `Deployment.build_from_flow` --> [`flow.deploy`](/api-ref/syntask/flows/#syntask.flows.Flow.deploy)

2. **Configuring remote flow code storage:**

    storage blocks --> [pull action](/concepts/deployments/#the-pull-action)

    When using the YAML-based deployment API, you can configure a pull action in your `syntask.yaml` file to specify how to retrieve flow code for your deployments. You can use configuration from your existing storage blocks to define your pull action [via templating](/guides/syntask-deploy/#templating-options).

    When using the Python deployment API, you can pass any storage block to the `flow.deploy` method to specify how to retrieve flow code for your deployment.

3. **Configuring flow run infrastructure:**

    infrastructure blocks --> [typed work pool](/concepts/work-pools/#worker-types)

    Default infrastructure config is now set on the typed work pool, and can be overwritten by individual deployments.

4. **Managing multiple deployments:**

    Create and/or update many deployments at once through a [`syntask.yaml`](/concepts/deployments/#working-with-multiple-deployments) file or use the [`deploy`](/api-ref/syntask/deployments/runner/#syntask.deployments.runner.deploy) function.

## What's similar

- Storage blocks can be set as the pull action in a `syntask.yaml` file.
- Infrastructure blocks have configuration fields similar to typed work pools.
- Deployment-level infrastructure overrides operate in much the same way.

    `infra_override` -> [`job_variable`](/concepts/deployments/#work-pool-fields)

- The process for starting an agent and [starting a worker](/concepts/work-pools/#starting-a-worker) in your environment are virtually identical.

    `syntask agent start --pool <work pool name>` --> `syntask worker start --pool <work pool name>`

    !!! Tip "Worker Helm chart"
        If you host your agents in a Kubernetes cluster, you can use the [Syntask worker Helm chart](https://github.com/Synopkg/syntask-helm/tree/main/charts/syntask-worker) to host workers in your cluster.

## Upgrade guide

If you have existing deployments that use infrastructure blocks, you can quickly upgrade them to be compatible with workers by following these steps:

1. **[Create a work pool](/concepts/work-pools/#work-pool-configuration)**

This new work pool will replace your infrastructure block.

You can use the [`.publish_as_work_pool`](/api-ref/syntask/infrastructure/#syntask.infrastructure.Infrastructure.publish_as_work_pool) method on any infrastructure block to create a work pool with the same configuration.

For example, if you have a `KubernetesJob` infrastructure block named 'my-k8s-job', you can create a work pool with the same configuration with this script:

```python
from syntask.infrastructure import KubernetesJob

KubernetesJob.load("my-k8s-job").publish_as_work_pool()
```

    Running this script will create a work pool named 'my-k8s-job' with the same configuration as your infrastructure block.

!!! Tip "Serving flows"
    If you are using a `Process` infrastructure block and a `LocalFilesystem` storage block (or aren't using an infrastructure and storage block at all), you can use [`flow.serve`](/api-ref/syntask/flows/#syntask.flows.Flow.deploy) to create a deployment without needing to specify a work pool name or start a worker.

    This is a quick way to create a deployment for a flow and is a great way to manage your deployments if you don't need the dynamic infrastructure creation or configuration offered by workers.

    Check out our [Docker guide](/guides/docker/) for how to build a served flow into a Docker image and host it in your environment.

2. **[Start a worker](/concepts/work-pools/#starting-a-worker)**

This worker will replace your agent and poll your new work pool for flow runs to execute.

<div class="terminal">
```bash
syntask worker start -p <work pool name>
```
</div>

3. **Deploy your flows to the new work pool**

To deploy your flows to the new work pool, you can use `flow.deploy` for a Pythonic deployment experience or `syntask deploy` for a YAML-based deployment experience.

If you currently use `Deployment.build_from_flow`, we recommend using `flow.deploy`.

If you currently use `syntask deployment build` and `syntask deployment apply`, we recommend using `syntask deploy`.

### `flow.deploy`

If you have a Python script that uses `Deployment.build_from_flow`, you can replace it with `flow.deploy`.

Most arguments to `Deployment.build_from_flow` can be translated directly to `flow.deploy`, but here are some changes that you may need to make:

- Replace `infrastructure` with `work_pool_name`.
  - If you've used the `.publish_as_work_pool` method on your infrastructure block, use the name of the created work pool.
- Replace `infra_overrides` with `job_variables`.
- Replace `storage` with a call to [`flow.from_source`](/api-ref/syntask/flows/#syntask.flows.Flow.deploy).
  - `flow.from_source` will load your flow from a remote storage location and make it deployable. Your existing storage block can be passed to the `source` argument of `flow.from_source`.

Below are some examples of how to translate `Deployment.build_from_flow` to `flow.deploy`.

#### Deploying without any blocks

If you aren't using any blocks:

```python
from syntask import flow

@flow(log_prints=True)
def my_flow(name: str = "world"):
    print(f"Hello {name}! I'm a flow from a Python script!")

if __name__ == "__main__":
    Deployment.build_from_flow(
        my_flow,
        name="my-deployment",
        parameters=dict(name="Marvin"),
    )
```

You can replace `Deployment.build_from_flow` with `flow.serve` :

```python
from syntask import flow

@flow(log_prints=True)
def my_flow(name: str = "world"):
    print(f"Hello {name}! I'm a flow from a Python script!")

if __name__ == "__main__":
    my_flow.serve(
        name="my-deployment",
        parameters=dict(name="Marvin"),
    )
```

This will start a process that will serve your flow and execute any flow runs that are scheduled to start.

#### Deploying using a storage block

If you currently use a storage block to load your flow code but no infrastructure block:

```python
from syntask import flow
from syntask.storage import GitHub

@flow(log_prints=True)
def my_flow(name: str = "world"):
    print(f"Hello {name}! I'm a flow from a GitHub repo!")

if __name__ == "__main__":
    Deployment.build_from_flow(
        my_flow,
        name="my-deployment",
        storage=GitHub.load("demo-repo"),
        parameters=dict(name="Marvin"),
    )
```

you can use `flow.from_source` to load your flow from the same location and `flow.serve` to create a deployment:

```python
from syntask import flow
from syntask.storage import GitHub

if __name__ == "__main__":
    flow.from_source(
        source=GitHub.load("demo-repo"),
        entrypoint="example.py:my_flow"
    ).serve(
        name="my-deployment",
        parameters=dict(name="Marvin"),
    )
```

This will allow you to execute scheduled flow runs without starting a worker. Additionally, the process serving your flow will regularly check for updates to your flow code and automatically update the flow if it detects any changes to the code.

#### Deploying using an infrastructure and storage block

For the code below, we'll need to create a work pool from our infrastructure block and pass it to `flow.deploy` as the `work_pool_name` argument. We'll also need to pass our storage block to `flow.from_source` as the `source` argument.

```python
from syntask import flow
from syntask.deployments import Deployment
from syntask.filesystems import GitHub
from syntask.infrastructure.kubernetes import KubernetesJob


@flow(log_prints=True)
def my_flow(name: str = "world"):
    print(f"Hello {name}! I'm a flow from a GitHub repo!")


if __name__ == "__main__":
    Deployment.build_from_flow(
        my_flow,
        name="my-deployment",
        storage=GitHub.load("demo-repo"),
        entrypoint="example.py:my_flow",
        infrastructure=KubernetesJob.load("my-k8s-job"),
        infra_overrides=dict(pull_policy="Never"),
        parameters=dict(name="Marvin"),
    )
```

The equivalent deployment code using `flow.deploy` would look like this:

```python
from syntask import flow
from syntask.storage import GitHub

if __name__ == "__main__":
    flow.from_source(
        source=GitHub.load("demo-repo"),
        entrypoint="example.py:my_flow"
    ).deploy(
        name="my-deployment",
        work_pool_name="my-k8s-job",
        job_variables=dict(pull_policy="Never"),
        parameters=dict(name="Marvin"),
    )
```

Note that when using `flow.from_source(...).deploy(...)`, the flow you're deploying does not need to be available locally before running your script.

#### Deploying via a Docker image

If you currently bake your flow code into a Docker image before deploying, you can use the `image` argument of `flow.deploy` to build a Docker image as part of your deployment process:

```python
from syntask import flow

@flow(log_prints=True)
def my_flow(name: str = "world"):
    print(f"Hello {name}! I'm a flow from a Docker image!")


if __name__ == "__main__":
    my_flow.deploy(
        name="my-deployment",
        image="my-repo/my-image:latest",
        work_pool_name="my-k8s-job",
        job_variables=dict(pull_policy="Never"),
        parameters=dict(name="Marvin"),
    )
```

You can skip a `flow.from_source` call when building an image with `flow.deploy`. Syntask will keep track of the flow's source code location in the image and load it from that location when the flow is executed.

### Using `syntask deploy`

!!! warning "Always run `syntask deploy` commands from the **root** level of your repo!"
    With agents, you might have had multiple `deployment.yaml` files, but under worker deployment patterns, each repo will have a single `syntask.yaml` file located at the **root** of the repo that contains [deployment configuration](/concepts/deployments/#working-with-multiple-deployments) for all flows in that repo.

To set up a new `syntask.yaml` file for your deployments, run the following command from the root level of your repo:

<div class="terminal">
```bash
syntask deploy
```
</div>

This will start a wizard that will guide you through setting up your deployment.

!!! Note "For step 4, select `y` on the last prompt to save the configuration for the deployment."
    Saving the configuration for your deployment will result in a `syntask.yaml` file populated with your first deployment. You can use this YAML file to edit and [define multiple deployments](/concepts/deployments/#working-with-multiple-deployments) for this repo.

You can add more [deployments](/concepts/deployments/#deployment-declaration-reference) to the `deployments` list in your `syntask.yaml` file and/or by continuing to use the deployment creation wizard.

For more information on deployments, check out our [in-depth guide for deploying flows to work pools](/guides/syntask-deploy/).
