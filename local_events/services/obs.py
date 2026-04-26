import typing
import logging

from obswebsocket import obsws, requests

from local_events.services.base import BaseService


class ObsService(BaseService):
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
        self.logger.debug('obs_client: start connect')
        self.client.connect()

    def version(self) -> None:
        return self.client.call(requests.GetVersion()).getObsVersion()

    def get_scenes(self):
        scenes = self.client.call(requests.GetSceneList())
        self.logger.debug('obs_client: get_scenes %s', scenes)
        return scenes.getScenes()

    def get_scene_item_list(self, scene_name: str) -> list[typing.Any]:
        self.logger.debug('obs_client: get_scene_item_list %s', scene_name)
        return self.client.call(
            requests.GetSceneItemList(sceneName=scene_name)
        ).getsceneItems()

    def set_source_filter_enabled(self, source_name: str, filter_name: str) -> None:
        self.logger.debug(
            'obs_client: set_source_filter_enabled %s %s', source_name, filter_name
        )
        result = self.client.call(
            requests.SetSourceFilterEnabled(
                sourceName=source_name,
                filterName=filter_name,
                filterEnabled=True,
            )
        )
        self.logger.debug('obs_client: result %s ', result)

    def set_source_filter_disabled(self, source_name: str, filter_name: str) -> None:
        self.logger.debug(
            'obs_client: set_source_filter_disabled %s %s', source_name, filter_name
        )
        result = self.client.call(
            requests.SetSourceFilterEnabled(
                sourceName=source_name,
                filterName=filter_name,
                filterEnabled=False,
            )
        )
        self.logger.debug('obs_client: result %s ', result)

    def _get_scene_item_id(self, scene_name: str, source_name: str) -> int:
        self.logger.debug(
            'obs_client: _get_scene_item_id %s %s', scene_name, source_name
        )
        items = self.get_scene_item_list(scene_name=scene_name)
        for item in items:
            if item.get('sourceName', '') == source_name:
                return item.get('sceneItemId', 0)
        self.logger.warning('cant get scene_item_id for %s %s', scene_name, source_name)
        return 0

    def scene_item_enabled(
        self,
        scene_name: str,
        source_name: str,
    ) -> None:
        scene_item_id = self._get_scene_item_id(scene_name, source_name)
        if not scene_item_id:
            self.logger.warning(
                'cant get scene_item_id for %s on %s', source_name, scene_name
            )
            return
        self._scene_item_enabled(scene_name, scene_item_id)

    def scene_item_disabled(
        self,
        scene_name: str,
        source_name: str,
    ) -> None:
        scene_item_id = self._get_scene_item_id(scene_name, source_name)
        if not scene_item_id:
            self.logger.warning(
                'cant get scene_item_id for %s on %s', source_name, scene_name
            )
            return
        self._scene_item_disabled(scene_name, scene_item_id)

    def _scene_item_enabled(
        self,
        scene_name: str,
        scene_item_id: int,
    ) -> None:
        self.client.call(
            requests.SetSceneItemEnabled(
                sceneName=scene_name,
                sceneItemId=scene_item_id,
                sceneItemEnabled=True,
            )
        )

    def _scene_item_disabled(
        self,
        scene_name: str,
        scene_item_id: int,
    ) -> None:
        self.client.call(
            requests.SetSceneItemEnabled(
                sceneName=scene_name,
                sceneItemId=scene_item_id,
                sceneItemEnabled=False,
            )
        )

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
