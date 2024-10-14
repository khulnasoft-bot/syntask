<p align="center"><img src="https://github.com/synopkg/syntask/assets/3407835/c654cbc6-63e8-4ada-a92a-efd2f8f24b85" width=1000></p>

<p align="center">
    <a href="https://pypi.python.org/pypi/syntask/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/syntask?color=0052FF&labelColor=090422"></a>
    <a href="https://github.com/synopkg/syntask/" alt="Stars">
        <img src="https://img.shields.io/github/stars/synopkg/syntask?color=0052FF&labelColor=090422" /></a>
    <a href="https://pepy.tech/badge/syntask/" alt="Downloads">
        <img src="https://img.shields.io/pypi/dm/syntask?color=0052FF&labelColor=090422" /></a>
    <a href="https://github.com/synopkg/syntask/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/synopkg/syntask?color=0052FF&labelColor=090422" /></a>
    <br>
    <a href="https://syntask.khulnasoft.com/slack" alt="Slack">
        <img src="https://img.shields.io/badge/slack-join_community-red.svg?color=0052FF&labelColor=090422&logo=slack" /></a>
    <a href="https://discourse.syntask.khulnasoft.com/" alt="Discourse">
        <img src="https://img.shields.io/badge/discourse-browse_forum-red.svg?color=0052FF&labelColor=090422&logo=discourse" /></a>
    <a href="https://www.youtube.com/c/SyntaskIO/" alt="YouTube">
        <img src="https://img.shields.io/badge/youtube-watch_videos-red.svg?color=0052FF&labelColor=090422&logo=youtube" /></a>
</p>

# Syntask

Syntask is a workflow orchestration framework for building data pipelines in Python.
It's the simplest way to elevate a script into a resilient production workflow.
With Syntask, you can build resilient, dynamic data pipelines that react to the world around them and recover from unexpected changes.

With just a few lines of code, data teams can confidently automate any data process with features such as scheduling, caching, retries, and event-based automations.

Workflow activity is tracked and can be monitored with a self-hosted [Syntask server](https://docs.syntask.khulnasoft.com/latest/manage/self-host/?utm_source=oss&utm_medium=oss&utm_campaign=oss_gh_repo&utm_term=none&utm_content=none) instance or managed [Syntask Cloud](https://www.syntask.khulnasoft.com/cloud-vs-oss?utm_source=oss&utm_medium=oss&utm_campaign=oss_gh_repo&utm_term=none&utm_content=none) dashboard.

## Getting started

Syntask requires Python 3.9 or later. To [install the latest or upgrade to the latest version of Syntask](https://docs.syntask.khulnasoft.com/get-started/install), run the following command:

```bash
pip install -U syntask
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
    github_stars(["SynoPKG/Syntask"])
```

Fire up the Syntask UI to see what happened:

```bash
syntask server start
```

To run your workflow on a schedule, turn it into a deployment and schedule it to run every minute by changing the last line of your script to the following:

```python
if __name__ == "__main__":
    github_stars.serve(name="first-deployment", cron="* * * * *", parameters={ "repos": ["SynoPKG/syntask"] })
```

You now have a server running locally that is looking for scheduled deployments!
Additionally you can run your workflow manually from the UI or CLI. You can even run deployments in response to [events](https://docs.syntask.khulnasoft.com/latest/automate/?utm_source=oss&utm_medium=oss&utm_campaign=oss_gh_repo&utm_term=none&utm_content=none).

## Syntask Cloud

Syntask Cloud provides workflow orchestration for the modern data enterprise. By automating over 200 million data tasks monthly, Syntask empowers diverse organizations — from Fortune 50 leaders such as Progressive Insurance to innovative disruptors such as Cash App — to increase engineering productivity, reduce pipeline errors, and cut data workflow compute costs.

Read more about Syntask Cloud [here](https://www.syntask.khulnasoft.com/cloud-vs-oss?utm_source=oss&utm_medium=oss&utm_campaign=oss_gh_repo&utm_term=none&utm_content=none) or sign up to [try it for yourself](https://app.syntask.cloud?utm_source=oss&utm_medium=oss&utm_campaign=oss_gh_repo&utm_term=none&utm_content=none).

## syntask-client

If your use case is geared towards communicating with Syntask Cloud or a remote Syntask server, check out our
[syntask-client](https://pypi.org/project/syntask-client/). It is a lighter-weight option for accessing client-side functionality in the Syntask SDK and is ideal for use in ephemeral execution environments.

## Next steps

- Check out the [Docs](https://docs.syntask.khulnasoft.com/).
- Join the [Syntask Slack community](https://syntask.khulnasoft.com/slack).
- Learn how to [contribute to Syntask](https://docs.syntask.khulnasoft.com/contribute/).
