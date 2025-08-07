from emcache import create_client, MemcachedHostAddress
import hashlib
import json
import asyncio
import gzip
from .utils import is_gzipped, logger
from .interfaces import EmcacheClientInterface
from typing import Optional

class EmcacheClient(EmcacheClientInterface):
    _client = None
    _lock = asyncio.Lock()
    _memcached_process = None
    _settings: Optional[MemcachedHostAddress] = None
    _timeout: int = 5  

    @classmethod
    def configure(cls, settings: MemcachedHostAddress, timeout: int = 5) -> None:
        """
        Configure the Memcached host and timeout. Must be called once before any cache operations.
        """
        cls._settings = settings
        cls._timeout = timeout

    @classmethod
    async def init_client(cls):
        if cls._settings is None:
            raise RuntimeError("EmcacheClient not configured; call configure() first")
        if cls._client is None:
            async with cls._lock:
                if cls._client is None:
                    cls._client = await create_client(
                        [cls._settings],
                        timeout=cls._timeout,
                    )
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None

    @classmethod
    async def get_client(cls):
        await cls.init_client()
        return cls._client

    @classmethod
    async def _gen_key(cls, key: str, prefix: str):
        digest = hashlib.sha256(key.encode()).hexdigest()
        return f"{prefix}:{digest}"
    
    @classmethod
    async def _get_registered_keys(cls, prefix: str):
        try:
            client = await cls.init_client()
            existing_keys_raw = await client.get(prefix.encode())
            if existing_keys_raw not in (None, b'') and existing_keys_raw.value is not None:
                return json.loads(existing_keys_raw.value.decode())
            return []
        except Exception as e:
            logger.error(f"[get_registered_keys] Failed to get registered keys for prefix: {prefix}", exc_info=True)
            return []
    
    @classmethod
    async def _register_key(cls, prefix: str, key: str):
        try:
            client = await cls.init_client()
            logger.info(f"[register_key] Registering key: {key} under prefix: {prefix}")

            existing_keys = await cls._get_registered_keys(prefix)

            if key not in existing_keys:
                existing_keys.append(key)
                await client.set(prefix.encode(), json.dumps(existing_keys).encode())
                logger.info(f"[register_key] Registered key: {key} under prefix: {prefix}")
        except Exception as e:
            logger.error(f"[register_key] Failed to register key: {key} under prefix: {prefix}", exc_info=True)

    @classmethod
    async def _unregister_key(cls, prefix: str, key: str):
        try:
            client = await cls.init_client()
            logger.info(f"[unregister_key] Unregistering key: {key} under prefix: {prefix}")

            existing_keys = await cls._get_registered_keys(prefix)

            if key in existing_keys:
                existing_keys.remove(key)
                await client.set(prefix.encode(), json.dumps(existing_keys).encode())
                logger.info(f"[unregister_key] Unregistered key: {key} under prefix: {prefix}")
        except Exception as e:
            logger.error(f"[unregister_key] Failed to unregister key: {key} under prefix: {prefix}", exc_info=True)
    
    @classmethod
    async def set(cls, key: str, value: dict | str, prefix: str = "", ttl: int = 3600 * 24 * 3):
        try:
            if value is None:
                logger.warning(f"[set] Value is None for key: {key}, skipping cache")
                return
            client = await cls.init_client()

            cache_key = await cls._gen_key(key, prefix)
            # await cls._register_key(prefix, cache_key)

            val = value
            if isinstance(val, dict):
                val = json.dumps(val)

            val = gzip.compress(val.encode())

            if len(val) > 1024 * 1024:
                logger.warning(f"[set] Compressed value too large for key: {key}, skipping cache")
                return

            await client.set(cache_key.encode(), val, exptime=ttl)
            logger.info(f"[set] Cached key: {cache_key} with TTL: {ttl} seconds")
        except Exception as e:
            logger.error(f"[set] Failed to set cache for key: {key}, prefix: {prefix}", exc_info=True)

    @classmethod
    async def get(cls, key: str, prefix: str = ""):
        try:
            client = await cls.init_client()

            cache_key = await cls._gen_key(key, prefix)
            logger.info(f"[get] Retrieving cache for key: {cache_key}")

            cached = await client.get(cache_key.encode())

            if cached is None:
                logger.info(f"[get] Cache miss for key: {cache_key}")
                return None

            if is_gzipped(cached.value):
                result = gzip.decompress(cached.value).decode()
            else:
                result = cached.value.decode()
            try:
                logger.info(f"[get] Cache hit for key: {cache_key}")
                return json.loads(result)
            except json.JSONDecodeError:
                logger.error(f"[get] Failed to decode JSON for key: {key}, result: {result}")
                return result
        except Exception as e:
            logger.error(f"[get] Failed to get cache for key: {key}, prefix: {prefix}", exc_info=True)
            return None
        
    @classmethod
    async def delete(cls, key: str, prefix: str = ""):
        try:
            client = await cls.init_client()

            cache_key = await cls._gen_key(key, prefix)
            logger.info(f"[delete] Deleting cache for key: {cache_key}")

            await client.delete(cache_key.encode())
            await cls._unregister_key(prefix, cache_key)

            logger.info(f"[delete] Deleted cache for key: {cache_key}")
        except Exception as e:
            logger.error(f"[delete] Failed to delete cache for key: {key}, prefix: {prefix}", exc_info=True)

    @classmethod
    async def delete_by_prefix(cls, prefix: str = ""):
        try:
            client = await cls.init_client()
            logger.info(f"[delete_by_prefix] Deleting cache for prefix: {prefix}")

            existing_keys = await cls._get_registered_keys(prefix)
            
            if not existing_keys:
                logger.info(f"[delete_by_prefix] No keys found for prefix: {prefix}")
                return
            
            tasks = [client.delete(key.encode()) for key in existing_keys]
            await asyncio.gather(*tasks)

            await client.delete(prefix.encode())
            logger.info(f"[delete_by_prefix] Deleted prefix key: {prefix}")
        except Exception as e:
            logger.error(f"[delete_by_prefix] Failed to delete cache with prefix: {prefix}", exc_info=True)
            return False