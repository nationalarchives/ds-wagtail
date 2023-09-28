from __future__ import annotations

from abc import ABC, abstractmethod


class APIModel(ABC):
    """Model representation of API data.."""

    @classmethod
    @abstractmethod
    def from_api_response(cls, response: dict) -> APIModel:
        """Transform a response From Client API into an APIModel instance.

        To be implemented the concrete class.
        """
        raise NotImplementedError
