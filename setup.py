from pathlib import Path

import versioneer
import setuptools
from setuptools import find_packages, setup

def read_requirements(file):
    requirements = []
    if Path(file).exists():
        requirements = open(file).read().strip().split("\n")
    return requirements


client_requires = read_requirements("requirements/requirements-client.txt")
install_requires = read_requirements("requirements/requirements.txt")[1:] + client_requires
dev_requires = read_requirements("requirements/requirements-dev.txt")

setup(
    # Package metadata
    name="syntask",
    description="Workflow orchestration and management.",
    author="KhulnaSoft, Ltd.",
    author_email="help@khulnasoft.com",
    url="https://www.syntask.khulnasoft.com",
    project_urls={
        "Changelog": "https://github.com/synopkg/syntask/releases",
        "Documentation": "https://docs.syntask.khulnasoft.com",
        "Source": "https://github.com/synopkg/syntask",
        "Tracker": "https://github.com/synopkg/syntask/issues",
    },
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # Versioning
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    # Package setup
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    # CLI
    entry_points={
        "console_scripts": ["syntask=syntask.cli:app"],
        "mkdocs.plugins": [
            "render_swagger = syntask.utilities.render_swagger:SwaggerPlugin",
        ],
    },
    # Requirements
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
        # Infrastructure extras
        "aws": "syntask-aws>=0.5.0rc1",
        "azure": "syntask-azure>=0.4.0rc1",
        "gcp": "syntask-gcp>=0.6.0rc1",
        "docker": "syntask-docker>=0.6.0rc1",
        "kubernetes": "syntask-kubernetes>=0.4.0rc1",
        "shell": "syntask-shell>=0.3.0rc1",
        # Distributed task execution extras
        "dask": "syntask-dask>=0.3.0rc1",
        "ray": "syntask-ray>=0.4.0rc1",
        # Version control extras
        "bitbucket": "syntask-bitbucket>=0.3.0rc1",
        "github": "syntask-github>=0.3.0rc1",
        "gitlab": "syntask-gitlab>=0.3.0rc1",
        # Database extras
        "databricks": "syntask-databricks>=0.3.0rc1",
        "dbt": "syntask-dbt>=0.6.0rc1",
        "snowflake": "syntask-snowflake>=0.28.0rc1",
        "sqlalchemy": "syntask-sqlalchemy>=0.5.0rc1",
        "redis": "syntask-redis>=0.2.0",
        # Monitoring extras
        "email": "syntask-email>=0.4.0rc1",
        "slack": "syntask-slack>=0.3.0rc1",
    },
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries",
    ],
)
