from __future__ import annotations

import itertools
from typing import AsyncIterator, Iterable, Iterator, Tuple, TypeVar

import requests

import toolforge_weld

T = TypeVar("T")

USER_AGENT = f"toolforge_weld/{toolforge_weld.__version__} python-requests/{requests.__version__}"


def peek(iterable: Iterator[T]) -> Tuple[T | None, Iterator[T]]:
    """Returns a tuple with the first element from an iterator and the iterator itself without consuming the first
    element."""
    try:
        first = next(iterable)
    except StopIteration:
        return None, iter([])
    return first, itertools.chain([first], iterable)


# These two could be provided by a third-party dependency (like aioitertools),
# but are simple enough that we just implement them here instead.
async def aiterator(iterator: Iterable[T]) -> AsyncIterator[T]:
    """Converts a non-async iterator into an async one."""
    for entry in iterator:
        yield entry


async def achain(*iterables: AsyncIterator[T]) -> AsyncIterator[T]:
    """Like functools.chain, but for async iterators."""
    for iterator in iterables:
        async for entry in iterator:
            yield entry


async def apeek(iterable: AsyncIterator[T]) -> Tuple[T | None, AsyncIterator[T]]:
    """Returns a tuple with the first element from an iterator and the iterator itself without consuming the first
    element."""
    try:
        first = await anext(iterable)
    except StopAsyncIteration:
        return None, aiterator([])
    return first, achain(aiterator([first]), iterable)
