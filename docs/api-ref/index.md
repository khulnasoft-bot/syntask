---
description: Explore Syntask's auto-generated reference documentation.
tags:
    - API
    - Syntask API
    - Syntask SDK
    - Syntask Cloud
    - REST API
    - development
    - orchestration
---

# API Reference

Syntask auto-generates reference documentation for the following components:

- **[Syntask Python SDK](/api-ref/python/)**: used to build, test, and execute workflows.
- **[Syntask REST API](/api-ref/rest-api/)**: used by both workflow clients as well as the Syntask UI for orchestration and data retrieval
  - Syntask Cloud REST API documentation is available at <a href="https://app.syntask.cloud/api/docs" target="_blank">https://app.syntask.cloud/api/docs</a>.
  - The REST API documentation for a locally hosted open-source Syntask server is available in the [Syntask REST API Reference](/api-ref/rest-api-reference/).
- **[Syntask Server SDK](/api-ref/server/)**: used primarily by the server to work with workflow metadata and enforce orchestration logic. This is only used directly by Syntask developers and contributors.

!!! Note "Self-hosted docs"
    When self-hosting, you can access REST API documentation at the `/docs` endpoint of your [`SYNTASK_API_URL`](/concepts/settings/#syntask_api_url) - for example, if you ran `syntask server start` with no additional configuration you can find this reference at <a href="http://localhost:4200/docs" target="_blank">http://localhost:4200/docs</a>.
