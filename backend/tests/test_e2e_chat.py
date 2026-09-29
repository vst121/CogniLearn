import asyncio
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check_e2e(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    
    # Assert exact expected schema and values
    assert response.json() == {
        "status": "healthy",
        "service": "CogniLearn AI Core",
        "version": "0.1.0"
    }

# @pytest.mark.asyncio
# async def test_rate_limiting_trigger(async_client: AsyncClient):
#     endpoint = "/api/v1/chat"
#     payload = {"query": "What is deep learning?", "course_code": "DL-101"}

#     # Fire 10 concurrent requests
#     responses = await asyncio.gather(
#         *(async_client.post(endpoint, json=payload) for _ in range(10))
#     )

#     # Ensure none of the first 10 requests were rate-limited
#     for res in responses:
#         assert res.status_code != 429, "Rate limit triggered too early"

#     # 11th request must be throttled
#     blocked_res = await async_client.post(endpoint, json=payload)
#     assert blocked_res.status_code == 429
#     assert "Rate limit exceeded" in blocked_res.json()["detail"]