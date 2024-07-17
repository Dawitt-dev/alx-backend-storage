#!/usr/bin/env python3
"""
This module implements a web cache and tracker.
"""

import redis
import requests
from typing import Callable

# Initialize the Redis client
redis_client = redis.Redis()


def cache_response(method: Callable) -> Callable:
    """
    Decorator to cache the response of the method for 10 seconds.
    """
    def wrapper(url: str) -> str:
        # Define the cache key and count key
        cache_key = f"cache:{url}"
        count_key = f"count:{url}"

        # Increment the count of the URL access
        redis_client.incr(count_key)

        # Check if the URL content is cached
        cached_content = redis_client.get(cache_key)
        if cached_content:
            return cached_content.decode("utf-8")

        # Fetch the content from the URL
        response = method(url)
        redis_client.setex(cache_key, 10, response)
        return response
    return wrapper


@cache_response
def get_page(url: str) -> str:
    """
    Get the HTML content of a particular URL and return it.

    Parameters
    ----------
    url : str
        The URL to fetch.

    Returns
    -------
    str
        The HTML content of the URL.
    """
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    # Test the get_page function
    url = "http://slowwly.robertomurray.co.uk"
    print(get_page(url))
    print(get_page(url))
    print(get_page(url))

    # Check the count of the URL accesses
    count_key = f"count:{url}"
    access_count = redis_client.get(count_key)
    print(f"Access count: {access_count.decode('utf-8')}")
