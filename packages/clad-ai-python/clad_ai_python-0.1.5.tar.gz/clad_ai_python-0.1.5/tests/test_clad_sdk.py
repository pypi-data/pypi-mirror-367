import pytest
import asyncio
import httpx
from unittest.mock import AsyncMock, patch
from clad_sdk import CladClient
import pytest_asyncio
# If you use redis-py async:
import redis.asyncio as aioredis

@pytest_asyncio.fixture
async def mock_redis():
    # Create an in-memory fake Redis using fakeredis OR a mocked client
    # Here: real aioredis instance pointing to local Redis
    r = aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
    await r.flushdb()
    yield r
    await r.flushdb()
    await r.close()

@pytest.fixture
def clad_with_local():
    # Local TTLCache only
    return CladClient(api_key="fake-key", threshold=2)

@pytest_asyncio.fixture
async def clad_with_redis(mock_redis):
    yield CladClient(api_key="fake-key", threshold=2, redis_client=mock_redis)


@pytest.mark.asyncio
async def test_ttl_cache_below_threshold(clad_with_local):
    user_id = "abc123"
    res1 = await clad_with_local.get_processed_input("hi", user_id)
    res2 = await clad_with_local.get_processed_input("hi again", user_id)

    assert res1["promptType"] == "clean"
    assert res2["promptType"] == "clean"
    assert clad_with_local._get_counter(user_id) == 2

@pytest.mark.asyncio
async def test_ttl_cache_crosses_threshold(clad_with_local, mocker):
    user_id = "abc123"
    clad_with_local.threshold = 3
    # Mock HTTP response for threshold crossing
    mock_response = {"prompt": "ads", "promptType": "injected"}
    mocker.patch("httpx.AsyncClient.get", new_callable=mocker.AsyncMock).return_value = AsyncMock(
        json=lambda: mock_response,
        raise_for_status=lambda: None
    )

    await clad_with_local.get_processed_input("hi", user_id)  # 1
    await clad_with_local.get_processed_input("hi2", user_id)  # 2
    res = await clad_with_local.get_processed_input("Im looking for a new coffee shop in Jose", user_id)  # 3+

    assert res["promptType"] == "injected"
    assert clad_with_local._get_counter(user_id) == 0  # should reset


@pytest.mark.asyncio
async def test_ttl_cache_api_error_fallback(clad_with_local, mocker):
    user_id = "abc123"
    fake_response = httpx.Response(500)
    fake_request = httpx.Request("GET", "http://testserver")
    mocker.patch(
        "httpx.AsyncClient.get",
        side_effect=httpx.HTTPStatusError("boom", request=fake_request, response=fake_response)
    )
    await clad_with_local.get_processed_input("hi", user_id)
    await clad_with_local.get_processed_input("hi2", user_id)
    res = await clad_with_local.get_processed_input("should fallback", user_id)

    assert res["promptType"] == "clean"

@pytest.mark.asyncio
async def test_fully_managed_passes_threshold(mocker):
    clad = CladClient(api_key="fake-key", threshold=2)
    user_id = "abc123"

    mock_response = {"prompt": "ads", "promptType": "injected"}
    mocker.patch("httpx.AsyncClient.get", new_callable=mocker.AsyncMock).return_value = AsyncMock(
        json=lambda: mock_response,
        raise_for_status=lambda: None
    )

    res = await clad.get_processed_input_fully_managed("hi", user_id, threshold=1)
    assert res["promptType"] == "injected"

@pytest.mark.asyncio
async def test_fully_managed_api_error(mocker):
    clad = CladClient(api_key="fake-key")
    user_id = "abc123"

    fake_response = httpx.Response(500)
    fake_request = httpx.Request("GET", "http://fake-url")
    mocker.patch(
        "httpx.AsyncClient.get",
        side_effect=httpx.HTTPStatusError("fail", request=fake_request, response=fake_response)
    )
    res = await clad.get_processed_input_fully_managed("hi", user_id)
    assert res["promptType"] == "clean"

@pytest.mark.asyncio
async def test_with_redis_below_threshold(clad_with_redis):
    user_id = "abc123"
    res1 = await clad_with_redis.get_processed_input_with_redis("hi", user_id)
    res2 = await clad_with_redis.get_processed_input_with_redis("hi2", user_id)

    val = await clad_with_redis._get_counter_redis(user_id)
    assert val == 2
    assert res1["promptType"] == "clean"
    assert res2["promptType"] == "clean"

@pytest.mark.asyncio
async def test_with_redis_crosses_threshold(clad_with_redis, mocker):
    user_id = "abc123"
    clad_with_redis.threshold = 1
    mock_response = {"prompt": "ads", "promptType": "injected"}
    mocker.patch("httpx.AsyncClient.get", new_callable=mocker.AsyncMock).return_value = AsyncMock(
        json=lambda: mock_response,
        raise_for_status=lambda: None
    )

    await clad_with_redis.get_processed_input_with_redis("hi", user_id)  # 1
    await clad_with_redis.get_processed_input_with_redis("hi2", user_id)  # 2
    res = await clad_with_redis.get_processed_input_with_redis("should trigger API", user_id)  # 3+

    val = await clad_with_redis._get_counter_redis(user_id)
    assert val == 0  # reset to 0
    assert res["promptType"] == "injected"

@pytest.mark.asyncio
async def test_with_redis_api_error(clad_with_redis, mocker):
    user_id = "abc123"
    req = httpx.Request("GET", "http://fake-url")
    res = httpx.Response(500, request=req)

    mocker.patch(
        "httpx.AsyncClient.get",
        side_effect=httpx.HTTPStatusError("fail", request=req, response=res)
    )
    await clad_with_redis.get_processed_input_with_redis("hi", user_id)
    await clad_with_redis.get_processed_input_with_redis("hi2", user_id)
    res = await clad_with_redis.get_processed_input_with_redis("should fallback", user_id)

    assert res["promptType"] == "clean"

@pytest.mark.asyncio
async def test_with_redis_debug_dump(clad_with_redis):
    user_id = "abc123"
    await clad_with_redis.get_processed_input_with_redis("hi", user_id)
    await clad_with_redis.get_processed_input_with_redis("hi again", user_id)

    # Confirm keys exist in Redis
    keys = await clad_with_redis._redis.keys("*")
    assert any("counter" in k for k in keys)
    assert any("context" in k for k in keys)

    counter = await clad_with_redis._get_counter_redis(user_id)
    context = await clad_with_redis._get_context_str_redis(user_id)
    assert counter > 0
    assert "User: hi" in context

@pytest.mark.asyncio
async def test_with_redis_missing_client():
    clad = CladClient(api_key="key", redis_client=None)
    with pytest.raises(RuntimeError):
        await clad.get_processed_input_with_redis("hi", "abc123")

@pytest.mark.asyncio
async def test_with_redis_fallback_to_local():
    # Make a fake Redis client that always raises
    bad_redis = AsyncMock()
    bad_redis.get.side_effect = Exception("Redis down")
    bad_redis.set.side_effect = Exception("Redis down")
    bad_redis.rpush.side_effect = Exception("Redis down")
    bad_redis.ltrim.side_effect = Exception("Redis down")
    bad_redis.lrange.side_effect = Exception("Redis down")

    clad = CladClient(api_key="fake-key", threshold=2, redis_client=bad_redis)

    user_id = "abc123"

    # Should fallback to local cache automatically
    res1 = await clad.get_processed_input_with_redis("hi", user_id)
    res2 = await clad.get_processed_input_with_redis("hi2", user_id)

    assert res1["promptType"] == "clean"
    assert res2["promptType"] == "clean"

    # Confirm fallback used local counter
    assert clad._get_counter(user_id) == 2
