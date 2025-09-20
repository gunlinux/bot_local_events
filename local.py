import asyncio
import logging

from requeue.requeue import Queue
from requeue.rredis import RedisConnection

from local_events import settings
from local_events.command_config import CommandConfig
from local_events.command_processor import CommandProcessor
from local_events.queue_consumer import QueueConsumer

logger = logging.getLogger('local_events')


async def main() -> None:
    redis_url: str = settings.local_events_redis_url
    async with RedisConnection(redis_url) as redis_connection:
        queue: Queue = Queue(name=settings.LOCAL_EVENTS, connection=redis_connection)
        command_config: CommandConfig = CommandConfig(settings.currencies)

        processor: CommandProcessor = CommandProcessor()

        local_events_consumer: QueueConsumer = QueueConsumer(
            command_config=command_config, processor=processor
        )
        print('yam yam yam')
        await queue.consumer(local_events_consumer.on_message)


if __name__ == '__main__':
    asyncio.run(main())
