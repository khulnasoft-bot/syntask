from syntask import flow
from syntask.logging import get_run_logger


@flow
def hello(name: str = "world"):
    get_run_logger().info(f"Hello {name}!")


if __name__ == "__main__":
    hello()
