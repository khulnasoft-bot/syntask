---
description: Answers to frequently asked questions about Syntask.
tags:
    - FAQ
    - frequently asked questions
    - questions
    - license
    - databases
---

# Frequently Asked Questions

## Syntask

### How is Syntask licensed?

Syntask is licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0), an [OSI approved](https://opensource.org/licenses/Apache-2.0) open-source license. If you have any questions about licensing, please [contact us](mailto:hello@syntask.io).

### Is the Syntask v2 Cloud URL different than the Syntask v1 Cloud URL?  

Yes. Syntask Cloud for v2 is at [app.syntask.cloud/](https://app.syntask.cloud) while Syntask Cloud for v1 is at [cloud.syntask.io](https://cloud.syntask.io/).

## The Syntask Orchestration Engine

### Why was the Syntask orchestration engine created?

The Syntask orchestration engine has three major objectives:

- Embracing dynamic, DAG-free workflows
- An extraordinary developer experience
- Transparent and observable orchestration rules

As Syntask has matured, so has the modern data stack. The on-demand, dynamic, highly scalable workflows that used to exist principally in the domain of data science and analytics are now prevalent throughout all of data engineering. Few companies have workflows that don’t deal with streaming data, uncertain timing, runtime logic, complex dependencies, versioning, or custom scheduling.

This means that the current generation of workflow managers are built around the wrong abstraction: the directed acyclic graph (DAG). DAGs are an increasingly arcane, constrained way of representing the dynamic, heterogeneous range of modern data and computation patterns.

Furthermore, as workflows have become more complex, it has become even more important to focus on the developer experience of building, testing, and monitoring them. Faced with an explosion of available tools, it is more important than ever for development teams to seek orchestration tools that will be compatible with any code, tools, or services they may require in the future.

And finally, this additional complexity means that providing clear and consistent insight into the behavior of the orchestration engine and any decisions it makes is critically important.

_The Syntask orchestration engine represents a unified solution to these three problems_.

The Syntask orchestration engine is capable of governing **any** code through a well-defined series of state transitions designed to maximize the user's understanding of what happened during execution. It's popular to describe "workflows as code" or "orchestration as code," but the Syntask engine represents "code as workflows": rather than ask users to change how they work to meet the requirements of the orchestrator, we've defined an orchestrator that adapts to how our users work.

To achieve this, we've leveraged the familiar tools of native Python: first class functions, type annotations, and `async` support. Users are free to implement as much &mdash; or as little &mdash; of the Syntask engine as is useful for their objectives.

### If I’m using Syntask Cloud 2, do I still need to run a Syntask server locally?

No, Syntask Cloud hosts an instance of the Syntask API for you. In fact, each workspace in Syntask Cloud corresponds directly to a single instance of the Syntask orchestration engine. See the [Syntask Cloud Overview](/ui/cloud/) for more information.


## Features

### Does Syntask support mapping?

Yes! For more information, see the [`Task.map` API reference](/api-ref/syntask/tasks/#syntask.tasks.Task.map)

```python
@flow
def my_flow():

    # map over a constant
    for i in range(10):
        my_mapped_task(i)

    # map over a task's output
    l = list_task()
    for i in l.wait().result():
        my_mapped_task_2(i)
```

Note that when tasks are called on constant values, they cannot detect their upstream edges automatically. In this example, `my_mapped_task_2` does not know that it is downstream from `list_task()`. Syntask will have convenience functions for detecting these associations, and Syntask's `.map()` operator will automatically track them.

### Can I enforce ordering between tasks that don't share data?

Yes! For more information, see the [`Tasks` section](/concepts/tasks/#wait-for).

### Does Syntask support proxies?

Yes!

Syntask supports communicating via proxies through the use of environment variables. You can read more about this in the [Installation](/getting-started/installation/#proxies) documentation and the article [Using Syntask Cloud with proxies](https://discourse.syntask.io/t/using-syntask-cloud-with-proxies/1696).

### Can I run Syntask flows on Linux?

Yes! 

See the [Installation](/getting-started/installation/) documentation and [Linux installation notes](/getting-started/installation/#linux-installation-notes) for details on getting started with Syntask on Linux.

### Can I run Syntask flows on Windows?

Yes!

See the [Installation](/getting-started/installation/) documentation and [Windows installation notes](/getting-started/installation/#windows-installation-notes) for details on getting started with Syntask on Windows.

### What external requirements does Syntask have?

Syntask does not have any additional requirements besides those installed by `pip install --pre syntask`. The entire system, including the UI and services, can be run in a single process via `syntask server start` and does not require Docker.

Syntask Cloud users do not need to worry about the Syntask database. Syntask Cloud uses PostgreSQL on GCP behind the scenes. To use PostgreSQL with a self-hosted Syntask server, users must provide the [connection string][syntask.settings.SYNTASK_API_DATABASE_CONNECTION_URL] for a running database via the `SYNTASK_API_DATABASE_CONNECTION_URL` environment variable.

### What databases does Syntask support?

A self-hosted Syntask server can work with SQLite and PostgreSQL. New Syntask installs default to a SQLite database hosted at `~/.syntask/syntask.db` on Mac or Linux machines. SQLite and PostgreSQL are not installed by Syntask.

### How do I choose between SQLite and Postgres?

SQLite generally works well for getting started and exploring Syntask. We have tested it with up to hundreds of thousands of task runs. Many users may be able to stay on SQLite for some time. However, for production uses, Syntask Cloud or self-hosted PostgreSQL is highly recommended. Under write-heavy workloads, SQLite performance can begin to suffer. Users running many flows with high degrees of parallelism or concurrency should use PostgreSQL.

## Relationship with other Syntask products

### Can a flow written with Syntask 1 be orchestrated with Syntask 2 and vice versa?

No. Flows written with the Syntask 1 client must be rewritten with the Syntask 2 client. For most flows, this should take just a few minutes. 
### Can I use Syntask 1 and Syntask 2 at the same time on my local machine?

Yes. Just use different virtual environments.
