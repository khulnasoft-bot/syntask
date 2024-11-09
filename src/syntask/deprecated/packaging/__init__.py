"""
DEPRECATION WARNING:
This module is deprecated as of March 2024 and will not be available after September 2024.
 """
from syntask.deprecated.packaging.docker import DockerPackager
from syntask.deprecated.packaging.file import FilePackager
from syntask.deprecated.packaging.orion import OrionPackager

# isort: split

# Register any packaging serializers
import syntask.deprecated.packaging.serializers
