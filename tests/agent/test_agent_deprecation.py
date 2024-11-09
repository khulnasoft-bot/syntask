import pytest

from syntask._internal.compatibility.deprecated import SyntaskDeprecationWarning
from syntask.agent import SyntaskAgent


def test_agent_emits_deprecation_warning():
    with pytest.warns(
        SyntaskDeprecationWarning,
        match=(
            "syntask.agent.SyntaskAgent has been deprecated. It will not be available after Sep 2024. Use a worker instead. Refer to the upgrade guide for more information"
        ),
    ):
        SyntaskAgent()
