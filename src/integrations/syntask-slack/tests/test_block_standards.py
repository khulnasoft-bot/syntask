import pytest

from syntask.blocks.core import Block
from syntask.testing.standard_test_suites import BlockStandardTestSuite
from syntask.utilities.dispatch import get_registry_for_type
from syntask.utilities.importtools import to_qualified_name


def find_module_blocks():
    blocks = get_registry_for_type(Block)
    module_blocks = [
        block
        for block in blocks.values()
        if to_qualified_name(block).startswith("syntask_slack")
    ]
    return module_blocks


@pytest.mark.parametrize("block", find_module_blocks())
class TestAllBlocksAdhereToStandards(BlockStandardTestSuite):
    @pytest.fixture
    def block(self, block):
        return block
