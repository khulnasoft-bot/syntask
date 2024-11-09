---
description: Observe and orchestrate your workflow applications with the hosted Syntask Cloud platform.
tags:
    - UI
    - dashboard
    - orchestration
    - Syntask Cloud
    - accounts
    - teams
    - workspaces
    - PaaS
title: Syntask Cloud
search:
  boost: 2
---

# Welcome to Syntask Cloud <span class="badge cloud"></span>

Syntask Cloud is a hosted workflow application framework that provides all the capabilities of Syntask server plus additional features, such as:

- automations, events, and webhooks so you can create event-driven workflows
- workspaces, RBAC, SSO, audit logs and related user management tools for collaboration
- push work pools for running flows on serverless infrastructure without a worker
- error summaries powered by Marvin AI to help you resolve errors faster

!!! success "Getting Started with Syntask Cloud"
    Ready to jump right in and start running with Syntask Cloud? See the [Quickstart](/getting-started/quickstart/) and follow the instructions on the **Cloud** tabs to write and deploy your first Syntask Cloud-monitored flow run.

![Viewing a workspace dashboard in the Syntask Cloud UI](/img/ui/cloud-dashboard.png)

Syntask Cloud includes all the features in the open-source Syntask server plus the following:

!!! cloud-ad "Syntask Cloud features"
    - [User accounts](#user-accounts) &mdash; personal accounts for working in Syntask Cloud.
    - [Workspaces](/cloud/workspaces/) &mdash; isolated environments to organize your flows, deployments, and flow runs.
    - [Automations](/cloud/automations/) &mdash; configure triggers, actions, and notifications in response to real-time monitoring events.
    - [Email notifications](/cloud/automations/) &mdash; send email alerts from Syntask's server based on automation triggers.
    - [Service accounts](/cloud/users/service-accounts/) &mdash; configure API access for running workers or executing flow runs on remote infrastructure.
    - [Custom role-based access controls (RBAC)](/cloud/users/roles/) &mdash; assign users granular permissions to perform certain activities within an account or a workspace.
    - [Single Sign-on (SSO)](/cloud/users/sso/) &mdash; authentication using your identity provider.
    - [Audit Log](/cloud/users/audit-log/) &mdash; a record of user activities to monitor security and compliance.
    - Collaboration &mdash; invite other people to your account.
    - Error summaries  &mdash; (enabled by Marvin AI) distill the error logs of `Failed` and `Crashed` flow runs into actionable information.
    - [Push work pools](/guides/deployment/push-work-pools/) &mdash; run flows on your serverless infrastructure without running a worker.

## User accounts

When you sign up for Syntask Cloud, an account and a user profile are automatically provisioned for you.

Your profile is the place where you'll manage settings related to yourself as a user, including:

- Profile, including profile handle and image
- API keys
- Preferences, including timezone and color mode

As an account Admin, you will also have access to account settings from the Account Settings page, such as:

- Members
- Workspaces
- Roles

As an account Admin you can create a [workspace](#workspaces) and invite other individuals to your workspace.

Upgrading from a Syntask Cloud Free tier plan to a Pro or Custom tier plan enables additional functionality for adding workspaces, managing teams, and running higher volume workloads.

Workspace Admins for Pro tier plans have the ability to set [role-based access controls (RBAC)](#roles-and-custom-permissions), view [Audit Logs](#audit-log), and configure [service accounts](#service-accounts).

Custom plans have [object-level access control lists](/cloud/users/object-access-control-lists/), [custom roles](/cloud/users/roles/), [teams](/cloud/users/teams/), and [single sign-on (SSO)](#single-sign-on-(sso) with [Directory Sync/SCIM provisioning](/cloud/users/sso/#scim-provisioning).

!!! cloud-ad "Syntask Cloud plans for teams of every size"
    See the [Syntask Cloud plans](https://www.syntask.io/pricing/) for details on Pro and Custom account tiers.

## Workspaces

A workspace is an isolated environment within Syntask Cloud for your flows, deployments, and block configuration.
See the [Workspaces](/cloud/workspaces/) documentation for more information about configuring and using workspaces.

Each workspace keeps track of its own:

- [Flow runs](/concepts/flows/) and task runs executed in an environment that is [syncing with the workspace](/cloud/workspaces/)
- [Flows](/concepts/flows/) associated with flow runs and deployments observed by the Syntask Cloud API
- [Deployments](/concepts/deployments/)
- [Work pools](/concepts/work-pools/)
- [Blocks](/concepts/blocks/) and [storage](/concepts/storage/)
- [Events](/cloud/events/)
- [Automations](/concepts/automations/)
- [Incidents](/cloud/incidents/)

![Viewing a workspace dashboard in the Syntask Cloud UI.](/img/ui/cloud-new-workspace.png)

## Events

Syntask Cloud allows you to see your [events](/cloud/events/). Events provide information about the state of your workflows, and can be used as [automation](/concepts/automations/) triggers.

![Syntask UI](/img/ui/event-feed.png)

## Automations

Syntask Cloud [automations](/concepts/automations/) provide additional notification capabilities beyond those in a self-hosted open-source Syntask server.
Automations also enable you to create event-driven workflows, toggle resources such as schedules and work pools, and declare incidents.

## Incidents <span class="badge pro"></span> <span class="badge custom"></span>

Syntask Cloud's [incidents](/cloud/incidents/) help teams identify, rectify, and document issues in mission-critical workflows.
Incidents are formal declarations of disruptions to a workspace.
With [automations](/cloud/incidents/#incident-automations)), activity in that workspace can be paused when an incident is created and resumed when it is resolved.

## Error summaries

Syntask Cloud error summaries, enabled by Marvin AI, distill the error logs of `Failed` and `Crashed` flow runs into actionable information.
To enable this feature and others powered by Marvin AI, visit the **Settings** page for your account.

## Service accounts <span class="badge pro"></span> <span class="badge custom"></span>

Service accounts enable you to create Syntask Cloud API keys that are not associated with a user account.
Service accounts are typically used to configure API access for running workers or executing flow runs on remote infrastructure.
See the [service accounts](/cloud/users/service-accounts/) documentation for more information about creating and managing service accounts.

## Roles and custom permissions <span class="badge pro"> </span><span class="badge custom"></span>

Role-based access controls (RBAC) enable you to assign users a role with permissions to perform certain activities within an account or a workspace.
See the [role-based access controls (RBAC)](/cloud/users/roles/) documentation for more information about managing user roles in a Syntask Cloud account.

## Single Sign-on (SSO) <span class="badge pro"></span> <span class="badge custom"></span>

Syntask Cloud's [Pro and Custom plans](https://www.syntask.io/pricing) offer [single sign-on (SSO)](/cloud/users/sso/) authentication integration with your team’s identity provider.
SSO integration can bet set up with identity providers that support OIDC and SAML.
Directory Sync and SCIM provisioning is also available with Custom plans.

## Audit log <span class="badge pro"></span> <span class="badge custom"></span>

Syntask Cloud's [Pro and Custom plans](https://www.syntask.io/pricing) offer [Audit Logs](/cloud/users/audit-log/) for compliance and security.
Audit logs provide a chronological record of activities performed by users in an account.

## Syntask Cloud REST API

The [Syntask REST API](/api-ref/rest-api/) is used for communicating data from Syntask clients to Syntask Cloud or a local Syntask server for orchestration and monitoring.
This API is mainly consumed by Syntask clients like the Syntask Python Client or the Syntask UI.

!!! note "Syntask Cloud REST API interactive documentation"
    Syntask Cloud REST API documentation is available at <a href="https://app.syntask.cloud/api/docs" target="_blank">https://app.syntask.cloud/api/docs</a>.

## Start using Syntask Cloud

To create an account or sign in with an existing Syntask Cloud account, go to [https://app.syntask.cloud/](https://app.syntask.cloud/).

Then follow the steps in the UI to deploy your first Syntask Cloud-monitored flow run. For more details, see the [Syntask Quickstart](/getting-started/quickstart/) and follow the instructions on the **Cloud** tabs.

!!! tip "Need help?"
    Get your questions answered by a Syntask Product Advocate!
    [Book a Meeting](https://calendly.com/syntask-experts/syntask-product-advocates?utm_campaign=syntask_docs_cloud&utm_content=syntask_docs&utm_medium=docs&utm_source=docs)
