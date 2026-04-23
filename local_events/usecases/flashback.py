from dataclasses import dataclass, field

from local_events.usecases.base import BaseUseCase
from local_events.integrations.obs import ObsClient


@dataclass
class FlashbackUsecase(BaseUseCase):
    duration: int = 30
    obs_client: ObsClient = field(default_factory=ObsClient)

    async def start(self) -> None:
        self.obs_client.set_source_filter_enabled(
            source_name='webcam_full', filter_name='gray'
        )
        self.obs_client.disconnect()

    async def finish(self) -> None:
        self.obs_client.connect()
        self.obs_client.set_source_filter_disabled(
            source_name='webcam_full', filter_name='gray'
        )
        self.obs_client.disconnect()
