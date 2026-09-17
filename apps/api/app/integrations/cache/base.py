from abc import ABC, abstractmethod


class CacheClient(ABC):
    @abstractmethod
    def ping(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError
