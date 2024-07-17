#!/usr/bin/env python3
"""
This module defines a Cache class for storing data in Redis.
"""

import redis
import uuid
from typing import Union


class Cache:
    """
    A Cache class that uses Redis to store data.

    Methods
    -------
    __init__():
        Initializes the Redis client and flushes the database.
    store(data: Union[str, bytes, int, float]) -> str:
        Stores the given data in Redis with a randomly generated key.
    """
    def __init__(self):
        """Initialize the Redis client and flush the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a random key and return the key.

        Parameters
        ----------
        data : Union[str, bytes, int, float]
            The data to store in Redis. It can be a string, bytes, integer,
            or float.

        Returns
        -------
        str
            The randomly generated key under which the data is stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key


if __name__ == "__main__":
    cache = Cache()

    data = b"hello"
    key = cache.store(data)
    print(f"Stored key: {key}")

    # Verifying the stored data
    local_redis = redis.Redis()
    stored_data = local_redis.get(key)
    print(f"Stored data: {stored_data}")
