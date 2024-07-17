#!/usr/bin/env python3
"""
This module defines a Cache class for storing data
in Redis, retrieving it while preserving the original type,
counting how many times methods are called, and
keeping a history of inputs and outputs.
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


def call_history(method: Callable) -> Callable:
    """
    Decorator that stores the history of inputs
    and outputs for a particular function.

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
        """Wrapper function that stores the input arguments
        and output of the method in Redis."""
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))

        return result
    return wrapper


class Cache:
    """
    A Cache class that uses Redis to store and
    retrieve data with original type preservation,
    count method calls, and store call history.

    Methods
    -------
    __init__():
        Initializes the Redis client and flushes the database.
    store(data: Union[str, bytes, int, float]) -> str:
        Stores the given data in Redis with a randomly generated key.
    get(key: str, fn: Optional[Callable]
    = None) -> Union[str, bytes, int, float, None]:
        Retrieves data from Redis and applies
        a conversion function if provided.
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
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a random key and return the key.

        Parameters
        ----------
        data : Union[str, bytes, int, float]
            The data to store in Redis. It can be
            a string, bytes, integer, or float.

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

    # Test cases for call history
    s1 = cache.store("first")
    print(s1)
    s2 = cache.store("second")
    print(s2)
    s3 = cache.store("third")
    print(s3)

    inputs = cache._redis.lrange(f"{cache.store.__qualname__}:inputs", 0, -1)
    outputs = cache._redis.lrange(f"{cache.store.__qualname__}:outputs", 0, -1)

    print(f"inputs: {inputs}")
    print(f"outputs: {outputs}")
