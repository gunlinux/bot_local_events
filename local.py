import asyncio

from dataclasses import dataclass
from collections.abc import Callable, Mapping

from faststream.rabbit import RabbitBroker
from local_events.integrations.obs import ObsClient
from requeue.fstream.models import FQueueMessage, FQueueEvent
from requeue.fstream.consumer import RabbitConsumer

from local_events import settings
from local_events.utils import logger_setup
from local_events import usecases

logger = logger_setup(__name__)

EVENTS_TO_PROCESS = [
    'CUSTOM_REWARD',
]


class Event:
    pass


@dataclass
class TwitchRewardEvent(Event):
    title: str


class EventHandler:
    def __init__(self, handlers: Mapping[type, Callable]) -> None:
        self.events: asyncio.Queue[Event] = asyncio.Queue()
        self.handlers = handlers

    def kill(self):
        raise asyncio.CancelledError

    async def add(self, event: Event) -> None:
        await self.events.put(event)

    async def event_worker(self) -> None:
        while 1:
            if event := await self.events.get():
                handler = self.handlers.get(type(event), None)
                self.run(handler, event=event)
            await asyncio.sleep(0.01)

    def run(self, handler: Callable | None, event: Event) -> None:
        if not handler:
            return
        loop = asyncio.get_running_loop()
        coro = handler(event)
        asyncio.run_coroutine_threadsafe(coro, loop)


@dataclass
class LocalConsumer:
    event_handler: EventHandler

    async def process_event(self, event: FQueueEvent) -> None:
        logger.info('got event %s', event)
        if event.event_type == 'CUSTOM_REWARD':
            if new_event := (
                TwitchRewardEvent(title=event.event.get('title', ''))
                if event.event
                else None
            ):
                logger.info('new custome reward %s', new_event)
                await self.event_handler.add(new_event)
            else:
                logger.info('cant get title')
            return
        logger.warning('cant get handler for %s', event)

    async def process(self, message: FQueueMessage) -> None:
        logger.info('get_mesage %s', message)
        if message.event in EVENTS_TO_PROCESS:
            await self.process_event(message.data)
            return
        logger.info('no reaseon to process %s', message)


@dataclass
class RewardRouter:
    obs_client: ObsClient

    async def reward_router(self, event: TwitchRewardEvent) -> None:
        if not event.title:
            return

        logger.critical('reward_router')
        match event.title:
            case 'flashback':
                await usecases.FlashbackUsecase(obs_client=self.obs_client).execute()
            case 'gpt_sucks':
                await usecases.GptsucksUsecase().execute()


async def main() -> None:
    broker = RabbitBroker(settings.rabbit_url, virtualhost=settings.rabbit_vhost)
    obs_client = ObsClient(password=settings.obs_password)

    reward_router = RewardRouter(obs_client=obs_client)

    handlers: Mapping[type, Callable] = {
        TwitchRewardEvent: reward_router.reward_router,
    }
    event_handler = EventHandler(handlers=handlers)
    local_events_consumer = LocalConsumer(event_handler=event_handler)
    consumer = RabbitConsumer(
        queue_name=settings.LOCAL_EVENTS,
        broker=broker,
        worker=local_events_consumer.process,
        after_shutdown=(event_handler.kill,),
    )

    try:
        await asyncio.gather(consumer.consume(), event_handler.event_worker())
    except asyncio.CancelledError:
        logger.info('this is fine')


if __name__ == '__main__':
    asyncio.run(main())
