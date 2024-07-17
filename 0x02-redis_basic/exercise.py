#!/usr/bin/env python3
"""
This module defines a Cache class for storing data in Redis.
"""

import redis
import uuid
from typing import Union, Callable, Optional


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

    def get(self, key: str, fn: Optional[Callable]
            = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and apply a conversion function if provided.

        Parameters
        ----------
        key : str
            The key for the data in Redis.
        fn : Optional[Callable], default None
            The function to convert the data back to the desired format.

        Returns
        -------
        Union[str, bytes, int, float, None]
            The retrieved data after applying the conversion function,
            or None if the key does not exist.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """
        Retrieve a string from Redis.

        Parameters
        ----------
        key : str
            The key for the data in Redis.

        Returns
        -------
        str
            The retrieved string data.
        """
        return self.get(key, lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """
        Retrieve an integer from Redis.

        Parameters
        ----------
        key : str
            The key for the data in Redis.

        Returns
        -------
        int
            The retrieved integer data.
        """
        return self.get(key, int)


if __name__ == "__main__":
    cache = Cache()

    # Test cases
    TEST_CASES = {
        b"foo": None,
        123: int,
        "bar": lambda d: d.decode("utf-8")
    }

    for value, fn in TEST_CASES.items():
        key = cache.store(value)
        assert cache.get(key, fn=fn) == value
        print(f"Test passed for value: {value}")

    print("All tests passed.")
