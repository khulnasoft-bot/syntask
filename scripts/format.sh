#!/usr/bin/env bash
set -x

ruff check src/syntask/ tests docs scripts benches --fix
ruff format src/syntask/ tests docs scripts benches