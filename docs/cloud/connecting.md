---
description: Configure a local execution environment to access Syntask Cloud.
tags:
    - Syntask Cloud
    - API keys
    - configuration
    - workers
    - troubleshooting
    - connecting
search:
  boost: 2
---

# Connecting & Troubleshooting Syntask Cloud <span class="badge cloud"></span>

To create flow runs in a local or remote execution environment and use either Syntask Cloud or a Syntask server as the backend API server, you need to  

- Configure the execution environment with the location of the API.
- Authenticate with the API, either by logging in or providing a valid API key (Syntask Cloud only).

## Log into Syntask Cloud from a terminal

Configure a local execution environment to use Syntask Cloud as the API server for flow runs. In other words, "log in" to Syntask Cloud from a local environment where you want to run a flow.

1. Open a new terminal session.
2. [Install Syntask](/getting-started/installation/) in the environment in which you want to execute flow runs.

<div class="terminal">
```bash
$ pip install -U syntask
```
</div>

3. Use the `syntask cloud login` Syntask CLI command to log into Syntask Cloud from your environment.

<div class="terminal">
```bash
$ syntask cloud login
```
</div>

The `syntask cloud login` command, used on its own, provides an interactive login experience. Using this command, you can log in with either an API key or through a browser.

<div class="terminal">
```bash
$ syntask cloud login
? How would you like to authenticate? [Use arrows to move; enter to select]
> Log in with a web browser
    Paste an API key
Paste your authentication key:
? Which workspace would you like to use? [Use arrows to move; enter to select]
> syntask/terry-syntask-workspace
    g-gadflow/g-workspace
Authenticated with Syntask Cloud! Using workspace 'syntask/terry-syntask-workspace'.
```
</div>

You can also log in by providing a [Syntask Cloud API key](../users/api-keys/) that you create.

### Change workspaces

If you need to change which workspace you're syncing with, use the `syntask cloud workspace set` Syntask CLI command while logged in, passing the account handle and workspace name.

<div class="terminal">
```bash
$ syntask cloud workspace set --workspace "syntask/my-workspace"
```
</div>

If no workspace is provided, you will be prompted to select one.

**Workspace Settings** also shows you the `syntask cloud workspace set` Syntask CLI command you can use to sync a local execution environment with a given workspace.

You may also use the `syntask cloud login` command with the `--workspace` or `-w` option to set the current workspace.

<div class="terminal">
```bash
$ syntask cloud login --workspace "syntask/my-workspace"
```
</div>

## Manually configure Syntask API settings

You can also manually configure the `SYNTASK_API_URL` setting to specify the Syntask Cloud API.

For Syntask Cloud, you can configure the `SYNTASK_API_URL` and `SYNTASK_API_KEY` settings to authenticate with Syntask Cloud by using an account ID, workspace ID, and API key.

<div class="terminal">
```bash
$ syntask config set SYNTASK_API_URL="https://api.syntask.cloud/api/accounts/[ACCOUNT-ID]/workspaces/[WORKSPACE-ID]"
$ syntask config set SYNTASK_API_KEY="[API-KEY]"
```
</div>

When you're in a Syntask Cloud workspace, you can copy the `SYNTASK_API_URL` value directly from the page URL.

In this example, we configured `SYNTASK_API_URL` and `SYNTASK_API_KEY` in the default profile. You can use `syntask profile` CLI commands to create settings profiles for different configurations. For example, you could have a "cloud" profile configured to use the Syntask Cloud API URL and API key, and another "local" profile for local development using a local Syntask API server started with `syntask server start`. See [Settings](/concepts/settings/) for details.

!!! note "Environment variables"
    You can also set `SYNTASK_API_URL` and `SYNTASK_API_KEY` as you would any other environment variable. See [Overriding defaults with environment variables](/concepts/settings/#overriding-defaults-with-environment-variables) for more information.

See the [Flow orchestration with Syntask](/tutorial/flows/) tutorial for examples.

## Install requirements in execution environments

In local and remote execution environments &mdash; such as VMs and containers &mdash; you must make sure any flow requirements or dependencies have been installed before creating a flow run.

# Troubleshooting Syntask Cloud

This section provides tips that may be helpful if you run into problems using Syntask Cloud.

## Syntask Cloud and proxies

Proxies intermediate network requests between a server and a client.

To communicate with Syntask Cloud, the Syntask client library makes HTTPS requests. These requests are made using the [`httpx`](https://www.python-httpx.org/) Python library. `httpx` respects accepted proxy environment variables, so the Syntask client is able to communicate through proxies.

To enable communication via proxies, simply set the `HTTPS_PROXY` and `SSL_CERT_FILE` environment variables as appropriate in your execution environment and things should “just work.”

See the [Using Syntask Cloud with proxies](https://discourse.syntask.io/t/using-syntask-cloud-with-proxies/1696) topic in Syntask Discourse for examples of proxy configuration.

URLs that should be whitelisted for outbound-communication in a secure environment include the UI, the API, Authentication, and the current OCSP server:  

- app.syntask.cloud
- api.syntask.cloud
- auth.workos.com
- api.github.com
- github.com
- ocsp.pki.goog/s/gts1d4/OxYEb8XcYmo

## Syntask Cloud access via API

If the Syntask Cloud API key, environment variable settings, or account login for your execution environment are not configured correctly, you may experience errors or unexpected flow run results when using Syntask CLI commands, running flows, or observing flow run results in Syntask Cloud.

Use the `syntask config view` CLI command to make sure your execution environment is correctly configured to access Syntask Cloud.

<div class="terminal">
```bash
$ syntask config view
SYNTASK_PROFILE='cloud'
SYNTASK_API_KEY='pnu_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' (from profile)
SYNTASK_API_URL='https://api.syntask.cloud/api/accounts/...' (from profile)
```
</div>

Make sure `SYNTASK_API_URL` is configured to use `https://api.syntask.cloud/api/...`.

Make sure `SYNTASK_API_KEY` is configured to use a valid API key.

You can use the `syntask cloud workspace ls` CLI command to view or set the active workspace.

<div class="terminal">
```bash
$ syntask cloud workspace ls
┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   Available Workspaces: ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━┩
│   g-gadflow/g-workspace │
│    * syntask/workinonit │
└─────────────────────────┘
    * active workspace
```
</div>

You can also check that the account and workspace IDs specified in the URL for `SYNTASK_API_URL` match those shown in the URL bar for your Syntask Cloud workspace.

## Syntask Cloud login errors

If you're having difficulty logging in to Syntask Cloud, the following troubleshooting steps may resolve the issue, or will provide more information when sharing your case to the support channel.

- Are you logging into Syntask Cloud 2? Syntask Cloud 1 and Syntask Cloud 2 use separate accounts. Make sure to use the right Syntask Cloud 2 URL: <https://app.syntask.cloud/>
- Do you already have a Syntask Cloud account? If you’re having difficulty accepting an invitation, try creating an account first using the email associated with the invitation, then accept the invitation.
- Are you using a single sign-on (SSO) provider, social authentication (Google, Microsoft, or GitHub) or just using an emailed link?

Other tips to help with login difficulties:

- Hard refresh your browser with Cmd+Shift+R.
- Try in a different browser. We actively test against the following browsers:
  - Chrome
  - Edge
  - Firefox
  - Safari
- Clear recent browser history/cookies

None of this worked?

Email us at <help@syntask.io> and provide answers to the questions above in your email to make it faster to troubleshoot and unblock you. Make sure you add the email address with which you were trying to log in, your Syntask Cloud account name, and, if applicable, the organization to which it belongs.
