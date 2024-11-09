---
description: Hosting Syntask Sever
tags:
    - UI
    - dashboard
    - Syntask Server
    - Observability
    - Events
    - Serve
    - Database
    - SQLite 
search:
  boost: 2
---

# Hosting a Syntask server instance

After you install Syntask you have a Python SDK client that can communicate with [Syntask Cloud](https://app.syntask.cloud), the platform hosted by Syntask. You also have an [API server](/api-ref/) instance backed by a database and a UI.

In this section you'll learn how to host your own Syntask server instance.
If you would like to host a Syntask server instance on Kubernetes, check out the syntask-server [Helm chart](https://github.com/Synopkg/syntask-helm/tree/main/charts/syntask-server).

Spin up a local Syntask server UI by running the `syntask server start` CLI command in the terminal:

<div class="terminal">
```bash
syntask server start
```
</div>

Open the URL for the Syntask server UI ([http://127.0.0.1:4200](http://127.0.0.1:4200) by default) in a browser.

![Viewing the dashboard in the Syntask UI.](/img/ui/self-hosted-server-dashboard.png)

Shut down the Syntask server with <kdb> ctrl </kbd> + <kdb> c </kbd> in the terminal.

### Differences between a self-hosted Syntask server instance and Syntask Cloud

A self-hosted Syntask server instance and Syntask Cloud share a common set of features. Syntask Cloud includes the following additional features:

- [Workspaces](/cloud/workspaces/) &mdash; isolated environments to organize your flows, deployments, and flow runs.
- [Automations](/cloud/automations/) &mdash; configure triggers, actions, and notifications in response to real-time monitoring events.
- [Email notifications](/cloud/automations/) &mdash; send email alerts from Syntask's servers based on automation triggers.
- [Service accounts](/cloud/users/service-accounts/) &mdash; configure API access for running workers or executing flow runs on remote infrastructure.
- [Custom role-based access controls (RBAC)](/cloud/users/roles/) &mdash; assign users granular permissions to perform activities within an account or workspace.
- [Single Sign-on (SSO)](/cloud/users/sso/) &mdash; authentication using your identity provider.
- [Audit Log](/cloud/users/audit-log/) &mdash; a record of user activities to monitor security and compliance.

You can read more about Syntask Cloud in the [Cloud](/cloud/) section.

### Configuring a Syntask server instance

Go to your terminal session and run this command to set the API URL to point to a Syntask server instance:

```bash
syntask config set SYNTASK_API_URL="http://127.0.0.1:4200/api"
```

!!! tip "`SYNTASK_API_URL` required when running Syntask inside a container"
    You must set the API server address to use Syntask within a container, such as a Docker container.

    You can save the API server address in a [Syntask profile](/concepts/settings/). Whenever that profile is active, the API endpoint will be be at that address.

    See [Profiles & Configuration](/concepts/settings/) for more information on profiles and configurable Syntask settings.

## Syntask database

The Syntask database persists data to track the state of your flow runs and related Syntask concepts, including:

- Flow run and task run state
- Run history
- Logs
- Deployments
- Flow and task run concurrency limits
- Storage blocks for flow and task results
- Variables
- Artifacts
- Work pool status

Currently Syntask supports the following databases:

- SQLite: The default in Syntask, and our recommendation for lightweight, single-server deployments. SQLite requires essentially no setup.
- PostgreSQL: Best for connecting to external databases, but does require additional setup (such as Docker). Syntask uses the [`pg_trgm`](https://www.postgresql.org/docs/current/pgtrgm.html) extension, so it must be installed and enabled.

### Using the database

A local SQLite database is the default database and is configured upon Syntask installation. The database is located at `~/.syntask/syntask.db` by default.

To reset your database, run the CLI command:  

<div class="terminal">
```bash
syntask server database reset -y
```
</div>

This command will clear all data and reapply the schema.

### Database settings

Syntask provides several settings for configuring the database. Here are the default settings:

<div class="terminal">
```bash
SYNTASK_API_DATABASE_CONNECTION_URL='sqlite+aiosqlite:///${SYNTASK_HOME}/syntask.db'
SYNTASK_API_DATABASE_ECHO='False'
SYNTASK_API_DATABASE_MIGRATE_ON_START='True'
SYNTASK_API_DATABASE_PASSWORD='None'
```
</div>

You can save a setting to your active Syntask profile with `syntask config set`.

### Configuring a PostgreSQL database

To connect Syntask to a PostgreSQL database, you can set the following environment variable:

<div class="terminal">
```bash
syntask config set SYNTASK_API_DATABASE_CONNECTION_URL="postgresql+asyncpg://postgres:yourTopSecretPassword@localhost:5432/syntask"
```
</div>

The above environment variable assumes that:

- You have a username called `postgres`
- Your password is set to `yourTopSecretPassword`
- Your database runs on the same host as the Syntask server instance, `localhost`
- You use the default PostgreSQL port `5432`
- Your PostgreSQL instance has a database called `syntask`

#### Quick start: configuring a PostgreSQL database with Docker 

To quickly start a PostgreSQL instance that can be used as your Syntask database, use the following command, which will start a Docker container running PostgreSQL:

<div class="terminal">
```bash
docker run -d --name syntask-postgres -v syntaskdb:/var/lib/postgresql/data -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=yourTopSecretPassword -e POSTGRES_DB=syntask postgres:latest
```
</div>

The above command:

- Pulls the [latest](https://hub.docker.com/_/postgres?tab=tags) version of the official `postgres` Docker image, which is compatible with Syntask.
- Starts a container with the name `syntask-postgres`.
- Creates a database `syntask` with a user `postgres` and `yourTopSecretPassword` password.
- Mounts the PostgreSQL data to a Docker volume called `syntaskdb` to provide persistence if you ever have to restart or rebuild that container.

Then you'll want to run the command above to set your current Syntask Profile to the PostgreSQL database instance running in your Docker container.

<div class="terminal">
```bash
syntask config set SYNTASK_API_DATABASE_CONNECTION_URL="postgresql+asyncpg://postgres:yourTopSecretPassword@localhost:5432/syntask"
```
</div>

### Confirming your PostgreSQL database configuration

Inspect your Syntask profile to confirm that the environment variable has been set properly:

<div class="terminal">
```bash
syntask config view --show-sources
```
</div>

<div class="terminal">
```bash
You should see output similar to the following:

SYNTASK_PROFILE='my_profile'
SYNTASK_API_DATABASE_CONNECTION_URL='********' (from profile)
SYNTASK_API_URL='http://127.0.0.1:4200/api' (from profile)
```
</div>

Start the Syntask server and it should begin to use your PostgreSQL database instance:

<div class="terminal">
```bash
syntask server start
```
</div>

### In-memory database

One of the benefits of SQLite is in-memory database support.

To use an in-memory SQLite database, set the following environment variable:

<div class="terminal">
```bash
syntask config set SYNTASK_API_DATABASE_CONNECTION_URL="sqlite+aiosqlite:///file::memory:?cache=shared&uri=true&check_same_thread=false"
```
</div>

!!! warning "Use SQLite database for testing only"
    SQLite is only supported by Syntask for testing purposes and is not compatible with multiprocessing.  

### Migrations

Syntask uses [Alembic](https://alembic.sqlalchemy.org/en/latest/) to manage database migrations. Alembic is a
database migration tool for usage with the SQLAlchemy Database Toolkit for Python. Alembic provides a framework for
generating and applying schema changes to a database.

To apply migrations to your database you can run the following commands:

To upgrade:

<div class="terminal">
```bash
syntask server database upgrade -y
```
</div>

To downgrade:

<div class="terminal">
```bash
syntask server database downgrade -y
```
</div>

You can use the `-r` flag to specify a specific migration version to upgrade or downgrade to.
For example, to downgrade to the previous migration version you can run:

<div class="terminal">
```bash
syntask server database downgrade -y -r -1
```
</div>

or to downgrade to a specific revision:

<div class="terminal">
```bash
syntask server database downgrade -y -r d20618ce678e
```
</div>

To downgrade all migrations, use the `base` revision.

See the [contributing docs](/contributing/overview/#adding-database-migrations) for information on how to create new database migrations.

## Notifications

When you use [Syntask Cloud](/cloud/) you gain access to a hosted platform with Workspace & User controls, Events, and Automations. Syntask Cloud has an option for automation notifications. The more limited Notifications option is provided for the self-hosted Syntask server.

Notifications enable you to set up alerts that are sent when a flow enters any state you specify. When your flow and task runs changes [state](/concepts/states/), Syntask notes the state change and checks whether the new state matches any notification policies. If it does, a new notification is queued.

Syntask supports sending notifications via:

- Slack message to a channel
- Microsoft Teams message to a channel
- Opsgenie to alerts
- PagerDuty to alerts
- Twilio to phone numbers
- Email (requires your own server)

!!! cloud-ad "Notifications in Syntask Cloud"
    Syntask Cloud uses the robust [Automations](/cloud/automations/) interface to enable notifications related to flow run state changes and work pool status.

### Configure notifications

To configure a notification in a Syntask server, go to the **Notifications** page and select **Create Notification** or the **+** button.

![Creating a notification in the Syntask UI](/img/ui/create-email-notification.png)

Notifications are structured just as you would describe them to someone. You can choose:

- Which run states should trigger a notification.
- Tags to filter which flow runs are covered by the notification.
- Whether to send an email, a Slack message, Microsoft Teams message, or other services.

For email notifications (supported on Syntask Cloud only), the configuration requires email addresses to which the message is sent.

For Slack notifications, the configuration requires webhook credentials for your Slack and the channel to which the message is sent.

For example, to get a Slack message if a flow with a `daily-etl` tag fails, the notification will read:

> If a run of any flow with **daily-etl** tag enters a **failed** state, send a notification to **my-slack-webhook**

When the conditions of the notification are triggered, you’ll receive a message:

> The **fuzzy-leopard** run of the **daily-etl** flow entered a **failed** state at **22-06-27 16:21:37 EST**.

On the **Notifications** page you can pause, edit, or delete any configured notification.

![Viewing all configured notifications in the Syntask UI](/img/ui/notifications.png)
