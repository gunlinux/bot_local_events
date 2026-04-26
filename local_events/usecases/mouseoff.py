from dataclasses import dataclass, field

from local_events.usecases.base import BaseUseCase
from local_events.integrations.shell import Shell
from local_events.services.sender import SenderService


@dataclass
class MouseoffUsecase(BaseUseCase):
    sender_client: SenderService
    duration: int = 60 * 10
    shell: Shell = field(default_factory=Shell)

    async def start(self) -> None:
        await self.shell.execute('mouse_off.sh')

    async def finish(self) -> None:
        await self.sender_client.send('Можно трогать мышку')
        await self.shell.execute('mouse_on.sh')
