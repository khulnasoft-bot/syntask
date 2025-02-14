"""
A service that checks for flow run notifications and sends them.
"""

import asyncio
from uuid import UUID

import sqlalchemy as sa

from syntask.server import models, schemas
from syntask.server.database.dependencies import inject_db
from syntask.server.database.interface import SyntaskDBInterface
from syntask.server.services.loop_service import LoopService
from syntask.utilities import urls


class FlowRunNotifications(LoopService):
    """
    A loop service that checks for flow run notifications that need to be sent.

    Notifications are queued, and this service pulls them off the queue and
    actually sends the notification.
    """

    # check queue every 4 seconds
    # note: a tight loop is executed until the queue is exhausted
    loop_seconds: int = 4

    @inject_db
    async def run_once(self, db: SyntaskDBInterface):
        while True:
            async with db.session_context(begin_transaction=True) as session:
                # Drain the queue one entry at a time, because if a transient
                # database error happens while sending a notification, the whole
                # transaction will be rolled back, which effectively re-queues any
                # notifications that we pulled here.  If we drain in batches larger
                # than 1, we risk double-sending earlier notifications when a
                # transient error occurs.
                notifications = await db.get_flow_run_notifications_from_queue(
                    session=session,
                    limit=1,
                )
                self.logger.debug(f"Got {len(notifications)} notifications from queue.")

                # if no notifications were found, exit the tight loop and sleep
                if not notifications:
                    break

                # all retrieved notifications are deleted, assert that we only got one
                # since we only send the first notification returned
                assert (
                    len(notifications) == 1
                ), "Expected one notification; query limit not respected."

                try:
                    await self.send_flow_run_notification(
                        session=session, db=db, notification=notifications[0]
                    )
                finally:
                    connection = await session.connection()
                    if connection.invalidated:
                        # If the connection was invalidated due to an error that we
                        # handled in _send_flow_run_notification, we'll need to
                        # rollback the session in order to synchronize it with the
                        # reality of the underlying connection before we can proceed
                        # with more iterations of the loop.  This may happen due to
                        # transient database connection errors, but will _not_
                        # happen due to an calling a third-party service to send a
                        # notification.
                        await session.rollback()
                        assert not connection.invalidated

    @inject_db
    async def send_flow_run_notification(
        self,
        session: sa.orm.session,
        db: SyntaskDBInterface,
        notification,
    ):
        try:
            orm_block_document = await session.get(
                db.BlockDocument, notification.block_document_id
            )
            if orm_block_document is None:
                self.logger.error(
                    f"Missing block document {notification.block_document_id} "
                    f"from policy {notification.flow_run_notification_policy_id}"
                )
                return

            from syntask.blocks.core import Block

            block = Block._from_block_document(
                await schemas.core.BlockDocument.from_orm_model(
                    session=session,
                    orm_block_document=orm_block_document,
                    include_secrets=True,
                )
            )

            message = self.construct_notification_message(notification=notification)
            await block.notify(
                subject="Syntask flow run notification",
                body=message,
            )

            self.logger.debug(
                "Successfully sent notification for flow run"
                f" {notification.flow_run_id} from policy"
                f" {notification.flow_run_notification_policy_id}"
            )

        except Exception:
            self.logger.error(
                (
                    "Error sending notification for policy"
                    f" {notification.flow_run_notification_policy_id} on flow run"
                    f" {notification.flow_run_id}"
                ),
                exc_info=True,
            )

    def construct_notification_message(self, notification) -> str:
        """
        Construct the message for a flow run notification, including
        templating any variables.
        """
        message_template = (
            notification.flow_run_notification_policy_message_template
            or models.flow_run_notification_policies.DEFAULT_MESSAGE_TEMPLATE
        )

        # create a dict from the sqlalchemy object for templating
        notification_dict = dict(notification._mapping)
        # add the flow run url to the info
        notification_dict["flow_run_url"] = self.get_ui_url_for_flow_run_id(
            flow_run_id=notification_dict["flow_run_id"]
        )

        message = message_template.format(
            **{
                k: notification_dict[k]
                for k in schemas.core.FLOW_RUN_NOTIFICATION_TEMPLATE_KWARGS
            }
        )
        return message

    def get_ui_url_for_flow_run_id(self, flow_run_id: UUID) -> str:
        """
        Returns a link to the flow run view of the given flow run id.

        Args:
            flow_run_id: the flow run id.
        """
        return urls.url_for(
            "flow-run",
            obj_id=flow_run_id,
            default_base_url="http://ephemeral-syntask/api",
        )


if __name__ == "__main__":
    asyncio.run(FlowRunNotifications(handle_signals=True).start())
