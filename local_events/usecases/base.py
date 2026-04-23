import asyncio


class BaseUseCase:
    duration: int = 0

    async def execute(self) -> None:
        await self.start()
        await self.wait()
        await self.finish()

    async def start(self) -> None: ...

    async def wait(self) -> None:
        if self.duration:
            await asyncio.sleep(self.duration)

    async def finish(self) -> None: ...
