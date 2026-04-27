from dataclasses import dataclass

from local_events.services.obs import ObsService
from local_events.usecases.base import BaseUseCase
from local_events.utils import logger_setup

logger = logger_setup(__name__)


@dataclass
class HelpUsecase(BaseUseCase):
    obs_client: ObsService
    duration: int = 8

    async def start(self) -> None:
        self.obs_client.connect()
        self.obs_client.scene_item_enabled('desktop', 'help')
        self.obs_client.disconnect()

    async def finish(self) -> None:
        self.obs_client.connect()
        self.obs_client.scene_item_disabled('desktop', 'help')
        self.obs_client.disconnect()
