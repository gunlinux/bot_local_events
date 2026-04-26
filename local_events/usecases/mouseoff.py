import asyncio
from dataclasses import dataclass, field

from local_events.usecases.base import BaseUseCase
from local_events.integrations.shell import Shell
from local_events.integrations.sender import SenderClient


@dataclass
class MouseoffUsecase(BaseUseCase):
    duration: int = 60 * 10
    shell: Shell = field(default_factory=Shell)
    sender_client: SenderClient = field(default_factory=SenderClient)

    async def start(self) -> None:
        await self.shell.execute('mouse_off.sh')

    async def finish(self) -> None:
        await self.sender_client.send('Можно трогать мышку')
        await self.shell.execute('mouse_on.sh')


if __name__ == '__main__':
    asyncio.run(MouseoffUsecase().execute())
