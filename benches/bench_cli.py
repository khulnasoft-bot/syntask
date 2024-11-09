import subprocess

from pytest_benchmark.fixture import BenchmarkFixture


def bench_syntask_help(benchmark: BenchmarkFixture):
    benchmark.pedantic(subprocess.check_call, args=(["syntask", "--help"],), rounds=3)


def bench_syntask_version(benchmark: BenchmarkFixture):
    benchmark.pedantic(subprocess.check_call, args=(["syntask", "version"],), rounds=3)


def bench_syntask_short_version(benchmark: BenchmarkFixture):
    benchmark.pedantic(
        subprocess.check_call, args=(["syntask", "--version"],), rounds=3
    )


def bench_syntask_profile_ls(benchmark: BenchmarkFixture):
    benchmark.pedantic(
        subprocess.check_call, args=(["syntask", "profile", "ls"],), rounds=3
    )
