import typing
import logging
from obswebsocket import obsws, requests


class ObsClient:
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 4455,
        password: str = '',
        logger: logging.Logger | None = None,
    ) -> None:
        self._host: str = host
        self._password: str = password
        self._port: int = port
        self.client = obsws(self._host, self._port, self._password)
        self.client.connect()
        self.logger = logger or logging.getLogger()

    def connect(self):
        self.client.connect()

    def version(self) -> None:
        return self.client.call(requests.GetVersion()).getObsVersion()

    def get_scenes(self):
        scenes = self.client.call(requests.GetSceneList())
        return scenes.getScenes()

    def get_scene_item_list(self, scene_name: str) -> list[typing.Any]:
        return self.client.call(
            requests.GetSceneItemList(sceneName=scene_name)
        ).getsceneItems()

    def set_source_filter_enabled(self, source_name: str, filter_name: str) -> None:
        _ = self.client.call(
            requests.SetSourceFilterEnabled(
                sourceName=source_name,
                filterName=filter_name,
                filterEnabled=True,
            )
        )

    def set_source_filter_disabled(self, source_name: str, filter_name: str) -> None:
        _ = self.client.call(
            requests.SetSourceFilterEnabled(
                sourceName=source_name,
                filterName=filter_name,
                filterEnabled=False,
            )
        )

    def scene_item_enable_state_changed(
        self,
        scene_name: str,
        scene_item_id: int,
        scene_item_enabled: bool,  # noqa: FBT001
    ) -> None:
        temp = self.client.call(
            requests.SetSceneItemEnabled(
                sceneName=scene_name,
                sceneItemId=scene_item_id,
                sceneItemEnabled=scene_item_enabled,
            )
        )
        print(temp)

    def get_source_filter(self, filter_name: str, source_uuid: int) -> int | None:
        if item := self.client.call(
            requests.GetSourceFilter(sourceUuid=source_uuid, filterName=filter_name)
        ):
            try:
                return item.getfilterIndex()
            except KeyError:
                return None
        return None

    def disconnect(self):
        self.client.disconnect()
