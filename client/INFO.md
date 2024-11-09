# Overview

This directory contains files for building and publishing the `syntask-client` 
library. `syntask-client` is built by removing source code from `syntask` and 
packages its own `requirements.txt` and `setup.py`. This process can happen 
in one of three ways:

- automatically whenever a PR is created (see 
`.github/workflows/syntask-client.yaml`)
- automatically whenever a Github release is published (see 
`.github/workflows/syntask-client-publish.yaml`)
- manually by running the `client/build_client.sh` script locally

Note that whenever a Github release is published the `syntask-client` will 
not only get built but will also be distributed to PyPI. `syntask-client` 
releases will have the same versioning as `syntask` - only the package names 
will be different.

This directory also includes a "minimal" flow that is used for smoke 
tests to ensure that the built `syntask-client` is functional.

In general, these builds, smoke tests, and publish steps should be transparent. 
It these automated steps fail, use the `client/build_client.sh` script to run 
the build and smoke test locally and iterate on a fix. The failures will likely 
be from:

- including a new dependency that is not installed in `syntask-client`
- re-arranging or adding files in such a way that a necessary file is rm'd at 
  build time
