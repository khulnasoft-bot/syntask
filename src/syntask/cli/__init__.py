import syntask.settings
from syntask._internal.compatibility.experimental import experiment_enabled
from syntask.cli.root import app

# Import CLI submodules to register them to the app
# isort: split

import syntask.cli.agent
import syntask.cli.artifact
import syntask.cli.block
import syntask.cli.cloud
import syntask.cli.cloud.webhook
import syntask.cli.shell
import syntask.cli.concurrency_limit
import syntask.cli.config
import syntask.cli.deploy
import syntask.cli.deployment
import syntask.cli.dev
import syntask.cli.flow
import syntask.cli.flow_run
import syntask.cli.kubernetes
import syntask.cli.profile
import syntask.cli.server
import syntask.cli.variable
import syntask.cli.work_pool
import syntask.cli.work_queue
import syntask.cli.worker
import syntask.cli.task_run
import syntask.events.cli.automations
