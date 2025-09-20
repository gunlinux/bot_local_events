import asyncio
import logging
from asyncio.subprocess import PIPE, Process

from local_events import settings

logger = logging.getLogger('local_events')


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
