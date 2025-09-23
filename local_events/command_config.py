import pathlib
import json
import typing
import logging

from requeue.models import QueueEvent


logger = logging.getLogger('local_events')
DEFAULT_COMMAND_PATH = './local_events/commands.json'


class CommandConfig:
    def __init__(
        self,
        currencices: dict[str, float],
        lcommands: list[dict[str, typing.Any]] | None = None,
        config_path: str = DEFAULT_COMMAND_PATH,
    ) -> None:
        self.currencices = currencices
        if config_path and lcommands is None:
            with pathlib.Path(config_path).open('r') as f:
                self.commands = json.load(f)
                print(self.commands)
        if lcommands:
            self.commands: list[dict[str, typing.Any]] = lcommands

    def _is_donate_by_message_and_price(
        self, command: dict[str, typing.Any], alert: QueueEvent
    ) -> bool:
        return (
            command['name'] in alert.message
            and alert.amount is not None
            and alert.amount > command['price']
            and command['type'] == 'donate'
            and alert.billing_system != 'TWITCH'
        )

    def _is_custom_reward(
        self, command: dict[str, typing.Any], alert: QueueEvent
    ) -> bool:
        return (
            alert.event_type == 'CUSTOM_REWARD'
            and alert.event is not None
            and alert.event.get('title', '') == command['name']
        )

    def _is_command_by_price(
        self, command: dict[str, typing.Any], alert: QueueEvent
    ) -> bool:
        if alert.currency != 'RUB' or not alert.amount:
            return False
        return command['type'] == 'bycash' and command['price'] == int(alert.amount)

    def _is_command_from_twitch(
        self, command: dict[str, typing.Any], alert: QueueEvent
    ) -> bool:
        return (
            alert.billing_system == 'RETWITCH'
            and command['type'] == 'twitch'
            and command['name'] == alert.message
        )

    def find(self, alert: QueueEvent) -> str | None:
        for command in self.commands:
            # donation alerts donate :D
            if (
                self._is_donate_by_message_and_price(command, alert)
                or self._is_command_from_twitch(command, alert)
                or self._is_command_by_price(command, alert)
                or self._is_custom_reward(command, alert)
            ):
                return command['command']
        return None
