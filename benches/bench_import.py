import importlib
import sys

import pytest
from prometheus_client import REGISTRY
from pytest_benchmark.fixture import BenchmarkFixture


def reset_imports():
    # Remove the module from sys.modules if it's there
    syntask_modules = [key for key in sys.modules if key.startswith("syntask")]
    for module in syntask_modules:
        del sys.modules[module]

    # Clear importlib cache
    importlib.invalidate_caches()

    # reset the prometheus registry to clear any previously measured metrics
    for collector in list(REGISTRY._collector_to_names):
        REGISTRY.unregister(collector)


@pytest.mark.benchmark(group="imports")
def bench_import_syntask(benchmark: BenchmarkFixture):
    def import_syntask():
        reset_imports()

        import syntask  # noqa

    benchmark(import_syntask)


@pytest.mark.timeout(180)
@pytest.mark.benchmark(group="imports")
def bench_import_syntask_flow(benchmark: BenchmarkFixture):
    def import_syntask_flow():
        reset_imports()

        from syntask import flow  # noqa

    benchmark(import_syntask_flow)
