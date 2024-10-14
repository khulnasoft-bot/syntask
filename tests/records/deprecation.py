from pathlib import Path

import pytest

from syntask.records.filesystem import FileSystemRecordStore
from syntask.records.memory import MemoryRecordStore
from syntask.records.result_store import ResultRecordStore
from syntask.results import get_result_store


def test_all_result_stores_emit_deprecation_warning():
    with pytest.warns(DeprecationWarning):
        ResultRecordStore(result_store=get_result_store())

    with pytest.warns(DeprecationWarning):
        MemoryRecordStore()

    with pytest.warns(DeprecationWarning):
        FileSystemRecordStore(records_directory=Path("foo"))
