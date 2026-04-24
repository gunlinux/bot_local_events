from faststream.rabbit import RabbitBroker
from requeue.sender.sender import Sender


class SenderClient:
    def __init__(
        self,
        broker: RabbitBroker | None = None,
        exchange_name: str = 'twitch_out',
    ) -> None:
        if broker is None:
            raise ValueError
        self.sender = Sender(exchange_name=exchange_name, broker=broker)

    async def send(self, message: str) -> None:
        await self.sender.send_message(message)
