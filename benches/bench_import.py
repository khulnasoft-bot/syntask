import subprocess

from pytest_benchmark.fixture import BenchmarkFixture


def bench_import_syntask(benchmark: BenchmarkFixture):
    benchmark.pedantic(
        subprocess.check_call, args=(["python", "-c", "import syntask"],), rounds=5
    )
