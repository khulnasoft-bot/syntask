---
description: Syntask Python client API for communicating with the Syntask REST API.
tags:
    - Python API
    - REST API
---

Asynchronous client implementation for communicating with the [Syntask REST API](/api-ref/rest-api/).

Explore the client by communicating with an in-memory webserver &mdash; no setup required:

<div class="terminal">
```
$ # start python REPL with native await functionality
$ python -m asyncio
>>> from syntask import get_client
>>> async with get_client() as client:
...     response = await client.hello()
...     print(response.json())
👋
```
</div>

::: syntask.client.orchestration
    options:
      filters: ["!^_", "!Config", "!copy", "!dict", "!json"]
      members_order: source
