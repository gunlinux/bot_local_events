import asyncio
from dataclasses import dataclass, field

from local_events.usecases.base import BaseUseCase
from local_events.integrations.shell import Shell


@dataclass
class GptsucksUsecase(BaseUseCase):
    duration: int = 60 * 10
    shell: Shell = field(default_factory=Shell)

    async def start(self) -> None:
        await self.shell.execute('gpt_off.sh')

    async def finish(self) -> None:
        await self.shell.execute('gpt_on.sh')


if __name__ == '__main__':
    asyncio.run(GptsucksUsecase().execute())
