import pytest

from syntask.blocks.core import Block
from syntask.testing.standard_test_suites import BlockStandardTestSuite
from syntask.utilities.dispatch import get_registry_for_type
from syntask.utilities.importtools import to_qualified_name

block_registry = get_registry_for_type(Block) or {}

blocks_under_test = [
    block
    for block in block_registry.values()
    if to_qualified_name(block).startswith("syntask.")
]


@pytest.mark.parametrize(
    "block", sorted(blocks_under_test, key=lambda x: x.get_block_type_slug())
)
class TestAllBlocksAdhereToStandards(BlockStandardTestSuite):
    @pytest.fixture
    def block(self, block):
        return block
