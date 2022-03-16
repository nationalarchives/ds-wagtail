from __future__ import annotations

from abc import ABC, abstractmethod

from django.conf import settings
from django.utils.functional import classproperty

from .client import KongClient
from .exceptions import DoesNotExist, MultipleObjectsReturned


class APIModel(ABC):
    """Model representation of API data.."""

    @classmethod
    @abstractmethod
    def from_api_response(cls, response: dict) -> APIModel:
        """Transform a response From Kong into an APIModel instance.

        To be implemented the concrete class.
        """
        raise NotImplementedError

    @classproperty
    def search(cls):
        raise DeprecationWarning(
            f"{cls.__name__}.search is deprecated. Use {cls.__name__}.api instead."
        )

    @classproperty
    def api(cls) -> APIManager:
        return APIManager(cls)


class APIManager:
    """Manager to fetch and transform a response into a model."""

    def __init__(self, model: APIModel):
        self.model: APIModel = model

    @property
    def client(self) -> KongClient:
        """Lazy-load client to allow tests to overwrite base url."""
        return KongClient(
            base_url=settings.KONG_CLIENT_BASE_URL,
            api_key=settings.KONG_CLIENT_KEY,
            verify_certificates=settings.KONG_CLIENT_VERIFY_CERTIFICATES,
        )

    def search(self, **kwargs) -> tuple[int, list[APIModel]]:
        """Make request to /search and transform the response."""
        response = self.client.search(**kwargs)
        count, hits = self._extract_hits_and_count(response)
        return count, [self.model.from_api_response(h) for h in hits]

    def search_unified(self, **kwargs) -> tuple[int, list[APIModel]]:
        """Make request to /searchUnified and transform the response."""
        response = self.client.search_unified(**kwargs)
        count, hits = self._extract_hits_and_count(response)
        return count, [self.model.from_api_response(h) for h in hits]

    def fetch(self, **kwargs) -> APIModel:
        """Make request to /fetch and transform the response."""
        response = self.client.fetch(**kwargs)
        count, hits = self._extract_hits_and_count(response)
        if count == 0:
            raise DoesNotExist
        if count > 1:
            raise MultipleObjectsReturned
        return self.model.from_api_response(hits[0])

    def fetch_all(self, **kwargs) -> tuple[int, list[APIModel]]:
        """Make request to /fetchAll and transform the response."""
        response = self.client.fetch_all(**kwargs)
        count, hits = self._extract_hits_and_count(response)
        return count, [self.model.from_api_response(h) for h in hits]

    def _extract_hits_and_count(self, response) -> tuple[int, list[dict]]:
        """Convenience method to extract results and count from a ES-like response."""
        total = response["hits"]["total"]["value"]
        hits = response["hits"]["hits"]

        return total, hits
