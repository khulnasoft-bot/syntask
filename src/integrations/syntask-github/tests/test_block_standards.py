import pytest
from syntask_github import GitHubCredentials, GitHubRepository

from syntask.testing.standard_test_suites import BlockStandardTestSuite


@pytest.mark.parametrize("block", [GitHubRepository, GitHubCredentials])
class TestAllBlocksAdhereToStandards(BlockStandardTestSuite):
    @pytest.fixture
    def block(self, block):
        return block
