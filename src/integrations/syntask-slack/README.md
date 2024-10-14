# syntask-slack

## Welcome!

`syntask-slack` is a collection of prebuilt Syntask tasks that can be used to quickly construct Syntask flows.

## Getting Started

### Python setup

Requires an installation of Python 3.9+

We recommend using a Python virtual environment manager such as pipenv, conda or virtualenv.

These tasks are designed to work with Syntask 2.0. For more information about how to use Syntask, please refer to the [Syntask documentation](https://docs.syntask.khulnasoft.com/).

### Installation

Install `syntask-slack`

```bash
pip install syntask-slack
```

### Slack setup

In order to use tasks in the collection, you'll first need to create an Slack app and install it in your Slack workspace. You can create a Slack app by navigating to the [apps page](https://api.slack.com/apps) for your Slack account and selecting 'Create New App'.

For tasks that require a Bot user OAuth token, you can get a token for your app by navigating to your apps __OAuth & Permissions__ page.

For tasks that require and Webhook URL, you get generate new Webhook URLs by navigating to you apps __Incoming Webhooks__ page.

Slack's [Basic app setup](https://api.slack.com/authentication/basics) guide provides additional details on setting up a Slack app.

### Write and run a flow

```python
from syntask import flow
from syntask.context import get_run_context
from syntask_slack import SlackCredentials
from syntask_slack.messages import send_chat_message


@flow
def example_send_message_flow():
   context = get_run_context()

   # Run other tasks and subflows here

   token = "xoxb-your-bot-token-here"
   send_chat_message(
         slack_credentials=SlackCredentials(token),
         channel="#syntask",
         text=f"Flow run {context.flow_run.name} completed :tada:"
   )

example_send_message_flow()
```
