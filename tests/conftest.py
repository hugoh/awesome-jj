import httpx2
import pytest


@pytest.fixture
async def client():
    """An unused-but-real AsyncClient, for functions that only pass it through to a fake fetcher."""
    async with httpx2.AsyncClient() as c:
        yield c
