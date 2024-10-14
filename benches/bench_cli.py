import subprocess

# It's hard to get a good reading on these in CodSpeed because they run in another process and
# CodSpeed currently doesn't include system calls in the benchmark time.
# TODO: Find a way to measure these in CodSpeed


def bench_syntask_help(benchmark):
    benchmark(subprocess.check_call, ["syntask", "--help"])


def bench_syntask_version(benchmark):
    benchmark(subprocess.check_call, ["syntask", "version"])


def bench_syntask_short_version(benchmark):
    benchmark(subprocess.check_call, ["syntask", "--version"])


def bench_syntask_profile_ls(benchmark):
    benchmark(subprocess.check_call, ["syntask", "profile", "ls"])
