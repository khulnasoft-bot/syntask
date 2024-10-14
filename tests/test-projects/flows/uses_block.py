import uuid

from syntask import flow
from syntask.blocks.system import Secret

block_name = f"foo-{uuid.uuid4()}"
Secret(value="bar").save("foo")

my_secret = Secret.load("foo")


@flow
async def uses_block():
    return my_secret.get()
