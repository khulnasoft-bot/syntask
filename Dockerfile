# The version of Python in the final image
ARG PYTHON_VERSION=3.9
# The base image to use for the final image; Syntask and its Python requirements will
# be installed in this image. The default is the official Python slim image.
# The following images are also available in this file:
#   syntask-conda: Derivative of continuum/miniconda3 with a 'syntask' environment. Used for the 'conda' flavor.
# Any image tag can be used, but it must have apt and pip.
ARG BASE_IMAGE=python:${PYTHON_VERSION}-slim
# The version used to build the Python distributable.
ARG BUILD_PYTHON_VERSION=3.9
# THe version used to build the UI distributable.
ARG NODE_VERSION=16.15
# Any extra Python requirements to install
ARG EXTRA_PIP_PACKAGES=""

# Build the Python distributable.
# Without this build step, versioneer cannot infer the version without git
# see https://github.com/python-versioneer/python-versioneer/issues/215
FROM python:${BUILD_PYTHON_VERSION}-slim AS python-builder

WORKDIR /opt/syntask

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    gpg \
    git=1:2.* \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the repository in; requires full git history for versions to generate correctly
COPY . ./

# Create a source distributable archive; ensuring existing dists are removed first
RUN rm -rf dist && python setup.py sdist
RUN mv "dist/$(python setup.py --fullname).tar.gz" "dist/syntask.tar.gz"


# Setup a base final image from miniconda
FROM continuumio/miniconda3 as syntask-conda

# Create a new conda environment with our required Python version
ARG PYTHON_VERSION
RUN conda create \
    python=${PYTHON_VERSION} \
    --name syntask

# Use the syntask environment by default
RUN echo "conda activate syntask" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]



# Build the final image with Syntask installed and our entrypoint configured
FROM ${BASE_IMAGE} as final

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

LABEL maintainer="help@khulnasoft.com"
LABEL io.syntask.python-version=${PYTHON_VERSION}
LABEL org.label-schema.schema-version = "1.0"
LABEL org.label-schema.name="syntask"
LABEL org.label-schema.url="https://www.syntask.khulnasoft.com/"

WORKDIR /opt/syntask

# Install requirements
# - tini: Used in the entrypoint
# - build-essential: Required for Python dependencies without wheels
# - git: Required for retrieving workflows from git sources
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    tini=0.19.* \
    build-essential \
    git=1:2.* \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Pin the pip version
RUN python -m pip install --no-cache-dir pip==23.3.1

# Install the base requirements separately so they cache
COPY requirements requirements
RUN pip install --upgrade --upgrade-strategy eager --no-cache-dir -r requirements/requirements.txt

# Install syntask from the sdist
COPY --from=python-builder /opt/syntask/dist ./dist

# Extras to include during `pip install`. Must be wrapped in brackets, e.g. "[dev]"
ARG SYNTASK_EXTRAS=${SYNTASK_EXTRAS:-""}
RUN pip install --no-cache-dir "./dist/syntask.tar.gz${SYNTASK_EXTRAS}"

ARG EXTRA_PIP_PACKAGES=${EXTRA_PIP_PACKAGES:-""}
RUN [ -z "${EXTRA_PIP_PACKAGES}" ] || pip install --no-cache-dir "${EXTRA_PIP_PACKAGES}"

# Smoke test
RUN syntask version

# Setup entrypoint
COPY scripts/entrypoint.sh ./entrypoint.sh
ENTRYPOINT ["/usr/bin/tini", "-g", "--", "/opt/syntask/entrypoint.sh"]
