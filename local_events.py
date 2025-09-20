import asyncio
import typing
import logging

from asyncio.subprocess import PIPE, Process

from requeue.requeue import Queue
from requeue.rredis import RedisConnection
from requeue.models import QueueMessage, QueueEvent

from local_events import settings
from local_events.commands import pay_commands  # pyright: ignore[reportMissingImports, reportUnknownVariableType]

logger = logging.getLogger('local_events')


class CommandConfig:
    def __init__(
        self, lcommands: list[dict[str, typing.Any]], currencices: dict[str, float]
    ) -> None:
        self.commands: list[dict[str, typing.Any]] = lcommands
        self.currencices = currencices

    def _is_donate_by_message_and_price(
        self, command: dict[str, typing.Any], alert: QueueEvent
    ) -> bool:
        return (
            command['name'] in alert.message
            and alert.amount > command['price']
            and command['type'] == 'donate'
            and alert.billing_system != 'TWITCH'
        )

    def _is_command_by_price(
        self, command: dict[str, typing.Any], alert: QueueEvent
    ) -> bool:
        if alert.currency != 'RUB' or not alert.amount:
            return False
        return command['type'] == 'bycash' and command['price'] == int(alert.amount)

    def _is_command_from_twitch(
        self, command: dict[str, typing.Any], alert: QueueEvent
    ) -> bool:
        return (
            alert.billing_system == 'RETWITCH'
            and command['type'] == 'twitch'
            and command['name'] == alert.message
        )

    def find(self, alert: QueueEvent) -> str | None:
        for command in self.commands:
            # donation alerts donate :D
            if (
                self._is_donate_by_message_and_price(command, alert)
                or self._is_command_from_twitch(command, alert)
                or self._is_command_by_price(command, alert)
            ):
                return command['command']
        return None


class CommandProcessor:
    def __init__(self, scripts_path: str = settings.scripts_path) -> None:
        # Define your valid commands and their corresponding scripts
        self.scripts_path: str = scripts_path

    async def stream_output(self, process: Process):
        while True:
            chunk = (
                await process.stdout.read(1024) if process.stdout is not None else False
            )  # Read chunks
            if not chunk:
                break
            print('STDOUT:', chunk.decode().strip())

    async def execute(self, command: str) -> bool:
        """Execute an external Python script in a subprocess"""
        logger.critical('kinda execute: %s', command)
        logger.critical('%s %s', self.scripts_path, command)

        # Prepare the command to run the script
        cmd = ['uv', 'run', f'{self.scripts_path}{command}']

        try:
            # Create subprocess
            process: Process = await asyncio.create_subprocess_exec(
                *cmd, stdout=PIPE, stderr=PIPE
            )
            task = asyncio.create_task(self.stream_output(process))
            _ = task.result()

        except Exception as e:  # noqa: BLE001
            logger.critical('Error executing script: %s', e)
            return False
        else:
            return True


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


async def main() -> None:
    redis_url: str = settings.local_events_redis_url
    async with RedisConnection(redis_url) as redis_connection:
        queue: Queue = Queue(name=settings.LOCAL_EVENTS, connection=redis_connection)
        command_config: CommandConfig = CommandConfig(pay_commands, settings.currencies)  # pyright: ignore[reportUnknownArgumentType]

        processor: CommandProcessor = CommandProcessor()

        local_events_consumer: QueueConsumer = QueueConsumer(
            command_config=command_config, processor=processor
        )
        print('yam yam yam')
        await queue.consumer(local_events_consumer.on_message)


if __name__ == '__main__':
    asyncio.run(main())
