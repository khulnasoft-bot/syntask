#!/bin/bash

CWD=$(pwd)

# if running in GH Actions, this will already be set
if [ -z ${TMPDIR+x} ];
    then
        TMPDIR=$(mktemp -d);
        echo "Using workspace at $TMPDIR";
    else echo "Using workspace at $TMPDIR";
fi

# init the workspace
cp -rf ./ $TMPDIR
cd $TMPDIR/src/syntask

# delete the files we don't need
rm -rf cli/
rm -rf deployments/recipes/
rm -rf deployments/templates
rm -rf server/__init__.py
find ./server \
    -not -path "./server" \
    -not -path "./server/api" \
    -not -path "./server/api/*" \
    -delete
rm -rf server/database
rm -rf server/models
rm -rf server/orchestration
rm -rf server/schemas
rm -rf server/services
rm -rf testing
rm -rf server/utilities

# replace old build files with client build files
cd $TMPDIR
cp client/setup.py .
cp client/README.md .

# if running in GH Actions, this happens in external workflow steps
# this is a convenience to simulate the full build locally
if [ -z ${CI} ];
    then
        if [[ -z "${SYNTASK_API_KEY}" ]] || [[ -z "${SYNTASK_API_URL}" ]]; then
            echo "In order to run smoke tests locally, SYNTASK_API_KEY and"\
            "SYNTASK_API_URL must be set and valid for a Syntask Cloud account.";
            exit 1;
        fi
        python -m venv venv;
        source venv/bin/activate;
        pip install wheel;
        python setup.py sdist bdist_wheel;
        pip install dist/*.tar.gz;
        python client/client_flow.py;
        echo "Build and smoke test completed successfully. Final results:";
        echo "$(du -sh $VIRTUAL_ENV)";
        deactivate;
    else echo "Skipping local build";
fi

cd $CWD
