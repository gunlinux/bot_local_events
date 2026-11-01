from faststream.rabbit import RabbitBroker, RabbitExchange

from local_events.models import FQueueMessage, FQueueEvent
from local_events.services.base import BaseService


class SenderService(BaseService):
    def __init__(
        self,
        broker: RabbitBroker | None = None,
        exchange_name: str = 'twitch_out',
    ) -> None:
        if broker is None:
            raise ValueError
        self.broker = broker
        self.exchange = RabbitExchange(exchange_name)
        self._connected = False

    async def _ensure_connected(self) -> None:
        if not self._connected:
            await self.broker.connect()
            self._connected = True

    async def send(self, message: str) -> None:
        await self._ensure_connected()
        new_message = FQueueMessage(
            event='mssg',
            source='',
            data=FQueueEvent(
                event_type='mssg',
                message=message,
            ),
        )
        await self.broker.publish(message=new_message, exchange=self.exchange)
