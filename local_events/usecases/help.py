from dataclasses import dataclass, field

from local_events.usecases.base import BaseUseCase
from local_events.integrations.obs import ObsClient
from local_events.utils import logger_setup

logger = logger_setup(__name__)


@dataclass
class HelpUsecase(BaseUseCase):
    duration: int = 8
    obs_client: ObsClient = field(default_factory=ObsClient)

    async def start(self) -> None:
        self.obs_client.connect()
        self.obs_client.scene_item_enabled('desktop', 'help')
        self.obs_client.disconnect()

    async def finish(self) -> None:
        self.obs_client.connect()
        self.obs_client.scene_item_disabled('desktop', 'help')
        self.obs_client.disconnect()
