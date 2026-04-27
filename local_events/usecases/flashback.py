from dataclasses import dataclass

from local_events.usecases.base import BaseUseCase
from local_events.services.obs import ObsService
from local_events.utils import logger_setup

logger = logger_setup(__name__)


@dataclass
class FlashbackUsecase(BaseUseCase):
    obs_client: ObsService
    duration: int = 30

    async def start(self) -> None:
        self.obs_client.connect()
        self.obs_client.set_source_filter_enabled(
            source_name='webcam_full', filter_name='gray'
        )
        self.obs_client.scene_item_enabled('desktop', 'flashback')
        self.obs_client.disconnect()

    async def finish(self) -> None:
        self.obs_client.connect()
        self.obs_client.set_source_filter_disabled(
            source_name='webcam_full', filter_name='gray'
        )
        self.obs_client.scene_item_disabled('desktop', 'flashback')
        self.obs_client.disconnect()
