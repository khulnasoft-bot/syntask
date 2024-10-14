import versioneer
from setuptools import find_packages, setup

install_requires = open("requirements-client.txt").read().strip().split("\n")

setup(
    # Package metadata
    name="syntask-client",
    description="Workflow orchestration and management.",
    author="Syntask Technologies, Inc.",
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
    # Requirements
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require={"notifications": ["apprise>=1.1.0, <2.0.0"]},
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
