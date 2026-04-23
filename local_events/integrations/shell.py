import asyncio
import logging
from asyncio.subprocess import Process, PIPE
from local_events import settings
from pathlib import Path


class Shell:
    def __init__(
        self,
        logger: logging.Logger | None = None,
        scripts_path: str = settings.scripts_path,
    ) -> None:
        # Define your valid commands and their corresponding scripts
        self.scripts_path: Path = Path(scripts_path)
        self.logger = logger or logging.getLogger()

    async def _stream_output(self, process: Process):
        while True:
            chunk = (
                await process.stdout.read(1024) if process.stdout is not None else False
            )  # Read chunks
            if not chunk:
                break
            print('STDOUT:', chunk.decode().strip())

    async def execute(self, command: str) -> bool:
        """Execute an external Python script in a subprocess"""
        self.logger.critical('kinda execute: %s', command)
        self.logger.critical('%s %s', self.scripts_path, command)

        # Prepare the command to run the script
        cmd = [f'{self.scripts_path / command}']

        try:
            # Create subprocess
            process: Process = await asyncio.create_subprocess_exec(
                *cmd, stdout=PIPE, stderr=PIPE
            )
            task = asyncio.create_task(self._stream_output(process))
            await task
            _ = task.result()

        except Exception as e:  # noqa: BLE001
            self.logger.critical('Error executing script: %s', e)
            return False
        return True
