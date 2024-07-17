#!/usr/bin/env python3
"""
This module defines a Cache class for storing
data in Redis, retrieving it while preserving the original type,
and counting how many times methods are called.
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator that counts how many times a method is called.

    Parameters
    ----------
    method : Callable
        The method to be decorated.

    Returns
    -------
    Callable
        The decorated method.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function that increments the call count in Redis."""
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


class Cache:
    """
    A Cache class that uses Redis to store and
    retrieve data with original type preservation.

    Methods
    -------
    __init__():
        Initializes the Redis client and flushes the database.
    store(data: Union[str, bytes, int, float]) -> str:
        Stores the given data in Redis with a randomly generated key.
    get(key: str, fn: Optional[Callable]
    = None) -> Union[str, bytes, int, float, None]:
        Retrieves data from Redis and
        applies a conversion function if provided.
    get_str(key: str) -> str:
        Retrieves a string from Redis.
    get_int(key: str) -> int:
        Retrieves an integer from Redis.
    """
    def __init__(self):
        """Initialize the Redis client and flush the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a random key and return the key.

        Parameters
        ----------
        data : Union[str, bytes, int, float]
            The data to store in Redis. It can be a
            string, bytes, integer, or float.

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
            The retrieved data after applying the
            conversion function, or None if the key does not exist.
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

    # Test cases for counting calls
    cache.store(b"first")
    print(cache.get(cache.store.__qualname__))  # Output should be 1

    cache.store(b"second")
    cache.store(b"third")
    print(cache.get(cache.store.__qualname__))  # Output should be 3
