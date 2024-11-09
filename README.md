<p align="center"><img src="https://github.com/Synopkg/syntask/assets/3407835/c654cbc6-63e8-4ada-a92a-efd2f8f24b85" width=1000></p>

<p align="center">
    <a href="https://pypi.python.org/pypi/syntask/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/syntask?color=0052FF&labelColor=090422"></a>
    <a href="https://github.com/syntaskhq/syntask/" alt="Stars">
        <img src="https://img.shields.io/github/stars/syntaskhq/syntask?color=0052FF&labelColor=090422" /></a>
    <a href="https://pepy.tech/badge/syntask/" alt="Downloads">
        <img src="https://img.shields.io/pypi/dm/syntask?color=0052FF&labelColor=090422" /></a>
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

# Syntask

Syntask is an orchestration and observability platform for building, observing, and triaging workflows. 
It's the simplest way to transform Python code into an interactive workflow application.

Syntask allows you to expose your workflows through an API so teams dependent on you can programmatically access your pipelines, business logic, and more.
Syntask also allows you to standardize workflow development and deployment across your organization.

With Syntask, you can build resilient, dynamic workflows that react to the world around them and recover from unexpected changes.
With just a few decorators, Syntask supercharges your code with features like automatic retries, distributed execution, scheduling, caching, and much more.

Every activity is tracked and can be monitored with a self-hosted [Syntask server](https://docs.syntask.io/latest/guides/host/) instance or managed [Syntask Cloud](https://www.syntask.io/cloud-vs-oss?utm_source=oss&utm_medium=oss&utm_campaign=oss_gh_repo&utm_term=none&utm_content=none) dashboard.

## Getting started

Syntask requires Python 3.8 or later. To [install Syntask](https://docs.syntask.io/getting-started/installation/), run the following command:

```bash
pip install syntask
```

Then create and run a Python file that uses Syntask `flow` and `task` decorators to orchestrate and observe your workflow - in this case, a simple script that fetches the number of GitHub stars from a repository:

```python
from syntask import flow, task
from typing import List
import httpx


@task(log_prints=True)
def get_stars(repo: str):
    url = f"https://api.github.com/repos/{repo}"
    count = httpx.get(url).json()["stargazers_count"]
    print(f"{repo} has {count} stars!")


@flow(name="GitHub Stars")
def github_stars(repos: List[str]):
    for repo in repos:
        get_stars(repo)


# run the flow!
if __name__=="__main__":
    github_stars(["Synopkg/Syntask"])
```

Fire up the Syntask UI to see what happened:

```bash
syntask server start
```

![Syntask UI dashboard](/docs/img/ui/cloud-dashboard.png)

To run your workflow on a schedule, turn it into a deployment and schedule it to run every minute by changing the last line of your script to the following:

```python
    github_stars.serve(name="first-deployment", cron="* * * * *")
```

You now have a server running locally that is looking for scheduled deployments!
Additionally you can run your workflow manually from the UI or CLI - and if you're using Syntask Cloud, you can even run deployments in response to [events](https://docs.syntask.io/latest/concepts/automations/).

## Syntask Cloud

Stop worrying about your workflows.
Syntask Cloud allows you to centrally deploy, monitor, and manage the data workflows you support. With managed orchestration, automations, and webhooks, all backed by enterprise-class security, build production-ready code quickly and reliably.

Read more about Syntask Cloud [here](https://www.syntask.io/cloud-vs-oss?utm_source=oss&utm_medium=oss&utm_campaign=oss_gh_repo&utm_term=none&utm_content=none) or sign up to [try it for yourself](https://app.syntask.cloud?utm_source=oss&utm_medium=oss&utm_campaign=oss_gh_repo&utm_term=none&utm_content=none).

![Syntask Automations](/docs/img/ui/automations.png)

## syntask-client

If your use case is geared towards communicating with Syntask Cloud or a remote Syntask server, check out our 
[syntask-client](https://pypi.org/project/syntask-client/). It was designed to be a lighter-weight option for accessing 
client-side functionality in the Syntask SDK and is ideal for use in ephemeral execution environments.

## Next steps

There's lots more you can do to orchestrate and observe your workflows with Syntask!
Start with our [friendly tutorial](https://docs.syntask.io/tutorials) or explore the [core concepts of Syntask workflows](https://docs.syntask.io/concepts/).

## Join the community

Syntask is made possible by the fastest growing community of thousands of friendly data engineers. Join us in building a new kind of workflow system. The [Syntask Slack community](https://syntask.io/slack) is a fantastic place to learn more about Syntask, ask questions, or get help with workflow design. All community forums, including code contributions, issue discussions, and slack messages are subject to our [Code of Conduct](https://discourse.syntask.io/faq).

## Contribute

See our [documentation on contributing to Syntask](https://docs.syntask.io/contributing/overview/).

Thanks for being part of the mission to build a new kind of workflow system and, of course, **happy engineering!**
