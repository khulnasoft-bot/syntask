---
description: Installing Syntask and configuring your environment
tags:
    - installation
    - pip install
    - development
    - Linux
    - Windows
    - SQLite
    - upgrading
search:
  boost: 2
---


# Installation

Syntask requires Python 3.8 or newer.

Python 3.12 support is experimental, as not all dependencies support Python 3.12 yet. If you encounter any errors, please [open an issue](https://github.com/Synopkg/syntask/issues/new?assignees=&labels=needs%3Atriage%2Cbug&projects=&template=1_general_bug_report.yaml).

<p align="left">
    <a href="https://pypi.python.org/pypi/syntask/" alt="Python Versions">
        <img src="https://img.shields.io/pypi/pyversions/syntask?color=0052FF&labelColor=090422" /></a>
    <a href="https://pypi.python.org/pypi/syntask/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/syntask?color=0052FF&labelColor=090422"></a>
</p>

We recommend installing Syntask using a Python virtual environment manager such as `pipenv`, `conda`, or `virtualenv`/`venv`.

!!! info "Windows and Linux requirements"
    See [Windows installation notes](#windows-installation-notes) and [Linux installation notes](#linux-installation-notes) for details on additional installation requirements and considerations.

## Install Syntask

The following sections describe how to install Syntask in your development or execution environment.

### Installing the latest version

Syntask is published as a Python package. To install the latest release or upgrade an existing Syntask install, run the following command in your terminal:

<div class="terminal">
```bash
pip install -U syntask
```
</div>

To install a specific version, specify the version number like this:

<div class="terminal">
```bash
pip install -U "syntask==2.16.2"
```
</div>

See available release versions in the [Syntask Release Notes](https://github.com/Synopkg/syntask/blob/main/RELEASE-NOTES.md).

### Installing the bleeding edge

If you'd like to test with the most up-to-date code, you can install directly off the `main` branch on GitHub:

<div class="terminal">
```bash
pip install -U git+https://github.com/Synopkg/syntask
```
</div>

!!! warning "The `main` branch may not be stable"
    Please be aware that this method installs unreleased code and may not be stable.

### Installing for development

If you'd like to install a version of Syntask for development:

1. Clone the [Syntask repository](https://github.com/Synopkg/syntask).
2. Install an editable version of the Python package with `pip install -e`.
3. Install pre-commit hooks.

<div class="terminal">
```bash
$ git clone https://github.com/Synopkg/syntask.git
$ cd syntask
$ pip install -e ".[dev]"
$ pre-commit install
```
</div>

See our [Contributing](/contributing/overview/) guide for more details about standards and practices for contributing to Syntask.

### Checking your installation

To confirm that Syntask was installed correctly, run the command `syntask version` to print the version and environment details to your console.

<div class="terminal">
```
$ syntask version

Version:             2.10.21
API version:         0.8.4
Python version:      3.10.12
Git commit:          da816542
Built:               Thu, Jul 13, 2023 2:05 PM
OS/Arch:             darwin/arm64
Profile:              local
Server type:         ephemeral
Server:
  Database:          sqlite
  SQLite version:    3.42.0

```
</div>

## Windows installation notes

You can install and run Syntask via Windows PowerShell, the Windows Command Prompt, or [`conda`](https://docs.conda.io/projects/conda/en/latest/user-guide/install/windows.html). After installation, you may need to manually add the Python local packages `Scripts` folder to your `Path` environment variable.

The `Scripts` folder path looks something like this (the username and Python version may be different on your system):

```bash
C:\Users\MyUserNameHere\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts
```

Watch the `pip install` output messages for the `Scripts` folder path on your system.

If you're using Windows Subsystem for Linux (WSL), see [Linux installation notes](#linux-installation-notes).

## Linux installation notes

Linux is a popular operating system for running Syntask. You can use [Syntask Cloud](/ui/cloud/) as your API server, or [host your own Syntask server](/host/) backed by [PostgreSQL](/concepts/database/#configuring_a_postgresql_database).

For development, you can use [SQLite](/concepts/database/#configuring_a_sqlite_database) 2.24 or newer as your database. Note that certain Linux versions of SQLite can be problematic. Compatible versions include Ubuntu 22.04 LTS and Ubuntu 20.04 LTS.

Alternatively, you can [install SQLite on Red Hat Custom Linux (RHEL)](#install-sqlite-on-rhel) or use the `conda` virtual environment manager and configure a compatible SQLite version.

## Using a self-signed SSL certificate

If you're using a self-signed SSL certificate, you need to configure your
environment to trust the certificate. You can add the
certificate to your system bundle and pointing your tools to use that bundle by configuring the `SSL_CERT_FILE` environment variable.

If the certificate is not part of your system bundle, you can set the
`SYNTASK_API_TLS_INSECURE_SKIP_VERIFY` to `True` to disable certificate verification altogether.

***Note:*** Disabling certificate validation is insecure and only suggested as an option for testing!

## Proxies

Syntask supports communicating via proxies through environment variables. Simply set `HTTPS_PROXY` and `SSL_CERT_FILE` in your environment, and the underlying network libraries will route Syntask’s requests appropriately. Read more about using Syntask Cloud with proxies [here](https://discourse.syntask.io/t/using-syntask-cloud-with-proxies/1696).

## External requirements

### SQLite

You can use [Syntask Cloud](/ui/cloud/) as your API server, or [host your own Syntask server](/host/) backed by [PostgreSQL](/concepts/database/#configuring_a_postgresql_database).

By default, a local Syntask server instance uses SQLite as the backing database. SQLite is not packaged with the Syntask installation. Most systems will already have SQLite installed, because it is typically bundled as a part of Python.

The Syntask CLI command `syntask version` prints environment details to your console, including the server database. For example:

<div class="terminal">
```
$ syntask version
Version:             2.10.21
API version:         0.8.4
Python version:      3.10.12
Git commit:          a46cbebb
Built:               Sat, Jul 15, 2023 7:59 AM
OS/Arch:             darwin/arm64
Profile:              default
Server type:         cloud
```
</div>

### Install SQLite on RHEL

The following steps are needed to install an appropriate version of SQLite on Red Hat Custom Linux (RHEL). Note that some RHEL instances have no C compiler, so you may need to check for and install `gcc` first:

<div class="terminal">
```bash
yum install gcc
```
</div>

Download and extract the tarball for SQLite.

<div class="terminal">
```bash
wget https://www.sqlite.org/2022/sqlite-autoconf-3390200.tar.gz
tar -xzf sqlite-autoconf-3390200.tar.gz
```
</div>

Move to the extracted SQLite directory, then build and install SQLite.

<div class="terminal">
```bash
cd sqlite-autoconf-3390200/
./configure
make
make install
```
</div>

Add `LD_LIBRARY_PATH` to your profile.

<div class="terminal">
```bash
echo 'export LD_LIBRARY_PATH="/usr/local/lib"' >> /etc/profile
```
</div>

Restart your shell to register these changes.

Now you can install Syntask using `pip`.

<div class="terminal">
```bash
pip3 install syntask
```
</div>

## Using Syntask in an environment with HTTP proxies

If you are using Syntask Cloud or hosting your own Syntask server instance, the Syntask library
will connect to the API via any proxies you have listed in the `HTTP_PROXY`,
`HTTPS_PROXY`, or `ALL_PROXY` environment variables.  You may also use the `NO_PROXY`
environment variable to specify which hosts should not be sent through the proxy.

For more information about these environment variables, see the [cURL
documentation](https://everything.curl.dev/usingcurl/proxies/env).

## Next steps

Now that you have Syntask installed and your environment configured, you may want to check out the [Tutorial](/tutorial/) to get more familiar with Syntask.
