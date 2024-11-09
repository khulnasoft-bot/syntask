---
description: Learn the basics of creating and running Syntask flows and tasks.
tags:
    - tutorial
    - getting started
    - basics
    - tasks
    - flows
    - subflows
    - deployments
    - workers
    - work pools
search:
  boost: 2
---
# Tutorial Overview

This tutorial provides a guided walk-through of Syntask core concepts and instructions on how to use them.

By the end of this tutorial you will have:

1. [Created a flow](/tutorial/flows/)
2. [Added tasks to it](/tutorial/tasks/)
3. [Deployed and run the flow locally](/tutorial/deployments/)
4. [Created a work pool and run the flow remotely](/tutorial/work-pools/)

These four topics will get most users to their first production deployment.

Advanced users that need more governance and control of their workflow infrastructure can go one step further by:

5. [Using a worker-based deployment](/tutorial/workers/)

If you're looking for examples of more advanced operations (like [deploying on Kubernetes](/guides/deployment/kubernetes/)), check out Syntask's [guides](/guides/).

## Prerequisites

1. Before you start, make sure you have Python installed, then install Syntask: `pip install -U syntask`

See the [install guide](/getting-started/installation/) for more detailed instructions, if needed.

2. To use Syntask, you need to self-host a Syntask server or connect to [Syntask Cloud](https://app.syntask.cloud).

To get the most out of this tutorial, we recommend using Syntask Cloud.
Sign up for a forever free [Syntask Cloud account](/cloud/) or accept your organization's invite to join their Syntask Cloud account.

1. Create a new account or sign in at [https://app.syntask.cloud/](https://app.syntask.cloud/).
1. Use the `syntask cloud login` CLI command to [authenticate to Syntask Cloud](/cloud/users/api-keys/) from your environment.

<div class="terminal">

```bash
syntask cloud login
```

</div>

Choose **Log in with a web browser** and click the **Authorize** button in the browser window that opens.

As an alternative to using Syntask Cloud, you can self-host a [Syntask server instance](/host/).
If you choose this option, run `syntask server start` to start a local Syntask server instance.

## What is Syntask?

Syntask orchestrates workflows — it simplifies the creation, scheduling, and monitoring of complex data pipelines.
With Syntask, you define workflows as Python code and let it handle the rest.

Syntask also provides error handling, retry mechanisms, and a user-friendly dashboard for monitoring.
It's the easiest way to transform any Python function into a unit of work that can be observed and orchestrated.

Just bring your Python code, sprinkle in a few decorators, and go!

## [First steps: Flows](/tutorial/flows/)

Let's begin by learning how to create your first Syntask flow - [click here to get started](/tutorial/flows/).
