#!/usr/bin/env bash

set -e
set -x

mypy src/syntask/
ruff check src/syntask/ tests docs scripts
ruff format src/syntask/ tests --check