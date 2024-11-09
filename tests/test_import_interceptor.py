import pytest


def test_syntask_1_import_warning():
    with pytest.raises(ImportError):
        with pytest.warns(UserWarning, match="Attempted import of 'syntask.Client"):
            from syntask import Client  # noqa
