from typing import ClassVar
from local_events.services.base import BaseService, ServiceProviderError


class ServiceProvider:
    _services: ClassVar[dict[str, BaseService]] = {}

    @classmethod
    def register(cls, name, service: BaseService):
        cls._services[name] = service

    @classmethod
    def get(cls, name) -> BaseService:
        if service := cls._services.get(name):
            return service
        raise ServiceProviderError
