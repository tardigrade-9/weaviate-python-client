from abc import ABC, abstractmethod
from typing import Dict, Optional

from proto.v1 import weaviate_pb2_grpc


class _ConnectionBase(ABC):
    @abstractmethod
    def get_current_bearer_token(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _get_additional_headers(self) -> Dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    def grpc_stub(self) -> Optional[weaviate_pb2_grpc.WeaviateStub]:
        raise NotImplementedError

    @abstractmethod
    def grpc_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_proxies(self) -> dict:
        raise NotImplementedError
