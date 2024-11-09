import os
import subprocess
import sys

from packaging.version import Version

import syntask


# Checks to make sure that collections are loaded prior to attempting to start a worker
def main():
    TEST_SERVER_VERSION = os.environ.get("TEST_SERVER_VERSION", syntask.__version__)
    # Work pool became GA in 2.8.0
    if Version(syntask.__version__) >= Version("2.8") and Version(
        TEST_SERVER_VERSION
    ) >= Version("2.8"):
        subprocess.check_call(
            ["python", "-m", "pip", "install", "syntask-kubernetes"],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        try:
            subprocess.check_output(
                ["syntask", "work-pool", "create", "test-pool", "-t", "nonsense"],
            )
        except subprocess.CalledProcessError as e:
            # Check that the error message contains kubernetes worker type
            for type in ["process", "kubernetes"]:
                assert type in str(
                    e.output
                ), f"Worker type {type!r} missing from output {e.output}"

        subprocess.check_call(
            ["syntask", "work-pool", "create", "test-pool", "-t", "kubernetes"],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        subprocess.check_call(
            [
                "syntask",
                "worker",
                "start",
                "-p",
                "test-pool",
                "-t",
                "kubernetes",
                "--run-once",
            ],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        subprocess.check_call(
            ["python", "-m", "pip", "uninstall", "syntask-kubernetes", "-y"],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        subprocess.check_call(
            ["syntask", "work-pool", "delete", "test-pool"],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )


if __name__ == "__main__":
    main()
