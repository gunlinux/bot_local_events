import logging

from requeue.models import QueueEvent, QueueMessage

from local_events.command_config import CommandConfig
from local_events.command_processor import CommandProcessor
from local_events import settings

logger = logging.getLogger('local_events')


class QueueConsumer:
    def __init__(
        self,
        processor: CommandProcessor,
        command_config: CommandConfig,
        timeout: int = 1,
    ):
        self.processor: CommandProcessor = processor
        self.timeout: int = timeout
        self.command_config: CommandConfig = command_config

    async def handle_event(self, event: QueueEvent) -> None:
        if command := self.command_config.find(event):
            logger.info('we found command: %s', command)
            _ = await self.processor.execute(command)
            return
        logger.critical('cant find a command %s', event)

    async def on_message(self, message: QueueMessage) -> QueueMessage | None:
        event: QueueEvent = message.data
        logger.info('start to handle_event %s', event)
        event.recal_amount(currencies=settings.currencies)
        await self.handle_event(event)
        return None
