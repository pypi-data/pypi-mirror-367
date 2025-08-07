from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from emcache import MemcachedHostAddress

class EmcacheClientInterface(ABC):
    """
    Defines the interface for a cache client implementation.
    """

    @classmethod
    @abstractmethod
    def configure(cls, settings: MemcachedHostAddress, timeout: int = 5) -> None:
        """
        Configure the cache client with connection settings and optional timeout.
        Must be called before any cache operations.
        """
        pass

    @classmethod
    @abstractmethod
    async def init_client(cls) -> Any:
        """
        Lazily initialize and return the underlying cache connection/client.
        Raises RuntimeError if not configured.
        """
        pass

    @classmethod
    @abstractmethod
    async def close(cls) -> None:
        """
        Close the underlying cache connection and clean up resources.
        """
        pass

    @classmethod
    @abstractmethod
    async def set(cls,
                  key: str,
                  value: Union[Dict[str, Any], str],
                  prefix: str = "",
                  ttl: int = 259200) -> None:
        """
        Store a value under the given key and prefix with a time-to-live in seconds.
        """
        pass

    @classmethod
    @abstractmethod
    async def get(cls,
                  key: str,
                  prefix: str = "") -> Optional[Union[Dict[str, Any], str]]:
        """
        Retrieve the cached value for the given key and prefix.
        Returns None on cache miss.
        """
        pass

    @classmethod
    @abstractmethod
    async def delete(cls,
                     key: str,
                     prefix: str = "") -> None:
        """
        Delete the cache entry for the given key and prefix.
        """
        pass

    @classmethod
    @abstractmethod
    async def delete_by_prefix(cls,
                               prefix: str = "") -> None:
        """
        Delete all cache entries registered under the given prefix.
        """
        pass
