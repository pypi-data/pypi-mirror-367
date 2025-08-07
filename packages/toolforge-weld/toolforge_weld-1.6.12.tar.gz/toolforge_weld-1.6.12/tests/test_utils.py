import pytest

from toolforge_weld.utils import aiterator, apeek, peek


def test_peek_data():
    first, iterator = peek(iter(["first", "second", "third"]))
    assert first == "first"
    assert list(iterator) == ["first", "second", "third"]


def test_peek_empty():
    first, iterator = peek(iter([]))
    assert first is None
    assert list(iterator) == []


@pytest.mark.asyncio
async def test_apeek_data():
    first, iterator = await apeek(aiterator(["first", "second", "third"]))
    assert first == "first"
    assert [entry async for entry in iterator] == ["first", "second", "third"]


@pytest.mark.asyncio
async def test_apeek_empty():
    first, iterator = await apeek(aiterator([]))
    assert first is None
    assert [entry async for entry in iterator] == []
