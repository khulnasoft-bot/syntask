<p align="center"><img src="https://github.com/Synopkg/syntask/assets/3407835/c654cbc6-63e8-4ada-a92a-efd2f8f24b85" width=1000></p>

<p align="center">
    <a href="https://pypi.python.org/pypi/syntask-client/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/syntask-client?color=0052FF&labelColor=090422"></a>
    <a href="https://github.com/syntaskhq/syntask/" alt="Stars">
        <img src="https://img.shields.io/github/stars/syntaskhq/syntask?color=0052FF&labelColor=090422" /></a>
    <a href="https://pepy.tech/badge/syntask-client/" alt="Downloads">
        <img src="https://img.shields.io/pypi/dm/syntask-client?color=0052FF&labelColor=090422" /></a>
    <a href="https://github.com/syntaskhq/syntask/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/syntaskhq/syntask?color=0052FF&labelColor=090422" /></a>
    <br>
    <a href="https://syntask.io/slack" alt="Slack">
        <img src="https://img.shields.io/badge/slack-join_community-red.svg?color=0052FF&labelColor=090422&logo=slack" /></a>
    <a href="https://discourse.syntask.io/" alt="Discourse">
        <img src="https://img.shields.io/badge/discourse-browse_forum-red.svg?color=0052FF&labelColor=090422&logo=discourse" /></a>
    <a href="https://www.youtube.com/c/SyntaskIO/" alt="YouTube">
        <img src="https://img.shields.io/badge/youtube-watch_videos-red.svg?color=0052FF&labelColor=090422&logo=youtube" /></a>
</p>

# syntask-client

The `syntask-client` package is a minimal-installation of `syntask` which is designed for interacting with Syntask Cloud 
or remote any `syntask` server. It sheds some functionality and dependencies in exchange for a smaller installation size, 
making it ideal for use in lightweight or ephemeral environments. These characteristics make it ideal for use in lambdas 
or other resource-constrained environments. 


## Getting started

`syntask-client` shares the same installation requirements as syntask. To install, make sure you are on Python 3.8 or 
later and run the following command:

```bash
pip install syntask-client
```

Next, ensure that your `syntask-client` has access to a remote `syntask` server by exporting the `SYNTASK_API_KEY` 
(if using Syntask Cloud) and `SYNTASK_API_URL` environment variables. Once those are set, use the package in your code as 
you would normally use `syntask`! 


For example, to remotely trigger a run a deployment:

```python
from syntask.deployments import run_deployment


def my_lambda(event):
    ...
    run_deployment(
        name="my-flow/my-deployment",
        parameters={"foo": "bar"},
        timeout=0,
    )

my_lambda({})
```

To emit events in an event driven system:

```python
from syntask.events import emit_event


def something_happened():
    emit_event("my-event", resource={"syntask.resource.id": "foo.bar"})

something_happened()
```


Or just interact with a `syntask` API:
```python
from syntask.client.orchestration import get_client


async def query_api():
    async with get_client() as client:
        limits = await client.read_concurrency_limits(limit=10, offset=0)
        print(limits)


query_api()
```


## Known limitations
By design, `syntask-client` omits all CLI and server components. This means that the CLI is not available for use 
and attempts to access server objects will fail. Furthermore, some classes, methods, and objects may be available 
for import in `syntask-client` but may not be "runnable" if they tap into server-oriented functionality. If you 
encounter such a limitation, feel free to [open an issue](https://github.com/Synopkg/syntask/issues/new/choose) 
describing the functionality you are interested in using and we will do our best to make it available.


## Next steps

There's lots more you can do to orchestrate and observe your workflows with Syntask!
Start with our [friendly tutorial](https://docs.syntask.io/tutorials) or explore the [core concepts of Syntask workflows](https://docs.syntask.io/concepts/).

## Join the community

Syntask is made possible by the fastest growing community of thousands of friendly data engineers. Join us in building a new kind of workflow system. The [Syntask Slack community](https://syntask.io/slack) is a fantastic place to learn more about Syntask, ask questions, or get help with workflow design. All community forums, including code contributions, issue discussions, and slack messages are subject to our [Code of Conduct](https://discourse.syntask.io/faq).

## Contribute

See our [documentation on contributing to Syntask](https://docs.syntask.io/contributing/overview/).

Thanks for being part of the mission to build a new kind of workflow system and, of course, **happy engineering!**
