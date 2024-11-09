---
description: Discover how to use the Syntask CLI for executing shell commands as flows.
tags:
    - CLI
    - Shell Commands
    - Syntask Flows
    - Automation
    - Scheduling
search:
  boost: 2
---

# Orchestrating Shell Commands with Syntask
Harness the power of the Syntask CLI to execute and schedule shell commands as Syntask flows. This guide shows how to use the `watch` and `serve` commands to showcase the CLI's versatility for automation tasks.

Here's what you'll learn:

- Running a shell command as a Syntask flow on-demand with `watch`.
- Scheduling a shell command as a recurring Syntask flow using `serve`.
- The benefits of embedding these commands into your automation workflows.

## Prerequisites
Before you begin, ensure you have:

- A basic understanding of Syntask flows. Start with the [Getting Started](/getting-started/quickstart/) guide if you're new.
- A recent version of Syntask installed in your command line environment. Follow the instructions in the [docs](/getting-started/installation/) if you have any issues.

## The `watch` command
The `watch` command wraps any shell command in a Syntask flow for instant execution, ideal for quick tasks or integrating shell scripts into your workflows.

### Example usage
Imagine you want to fetch the current weather in Chicago using the `curl` command. The following Syntask CLI command does just that:

```bash
syntask shell watch "curl http://wttr.in/Chicago?format=3"
```

This command makes a request to `wttr.in`, a console-oriented weather service, and prints the weather conditions for Chicago.

### Benefits of `watch`
- **Immediate feedback:** Execute shell commands  within the Syntask framework for immediate results.
- **Easy integration:** Seamlessly blend external scripts or data fetching into your data workflows.
- **Visibility and logging:** Leverage Syntask's logging to track the execution and output of your shell tasks.

## Deploying with `serve`
When you need to run shell commands on a schedule, the `serve` command creates a Syntask [deployment](/concepts/deployments/ for regular execution. This is an extremely quick way to create a deployment that is served by Syntask.

### Example usage
To set up a daily weather report for Chicago at 9 AM, you can use the `serve` command as follows:

```bash
syntask shell serve "curl http://wttr.in/Chicago?format=3" --flow-name "Daily Chicago Weather Report" --cron-schedule "0 9 * * *" --deployment-name "Chicago Weather"
```

This command schedules a Syntask flow to fetch Chicago's weather conditions daily, providing consistent updates without manual intervention. Additionally, if you want to fetch the Chicago weather, you can manually create a run of your new deployment from the UI or the CLI.

To shut down your server and pause your scheduled runs, hit `ctrl` + `c` in the CLI.

### Benefits of `serve`
- **Automated scheduling:** Schedule shell commands to run automatically, ensuring critical updates are generated and available on time.
- **Centralized workflow management:** Manage and monitor your scheduled shell commands inside Syntask for a unified workflow overview.
- **Configurable execution:** Tailor execution frequency, [concurrency limits](/guides/global-concurrency-limits/), and other parameters to suit your project's needs and resources.

## Next steps
With the `watch` and `serve` commands at your disposal, you're ready to incorporate shell command automation into your Syntask workflows. You can start with straightforward tasks like observing cron jobs and expand to more complex automation scenarios to enhance your workflows' efficiency and capabilities.

Check out the [tutorial](/tutorial/) and explore other Syntask docs to learn how to gain more observability and orchestration capabilities in your workflows. 
