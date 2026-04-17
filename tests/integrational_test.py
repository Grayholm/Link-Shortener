from httpx import AsyncClient
import pytest


@pytest.mark.parametrize(
    "long_url, should_raise, expected_status_code",
    [
        ("https://www.example.com/", False, 302),
        ("https://www.google.com/", False, 302),
        ("invalid-url", True, 422),
        ("", True, 422),
        ("https://www.example.com/", True, 404),
    ],
)
async def test_redirect_to_url_API(
    ac: AsyncClient, long_url, should_raise, expected_status_code
):
    create_response = await ac.post("/api/short-links", json={"long_url": long_url})
    if create_response.status_code == 422:
        assert should_raise
        return
    assert create_response.status_code == 200
    slug = create_response.json()["slug"]

    if should_raise:
        redirect_response = await ac.get("/api/short-links/FGGg46")
        assert redirect_response.status_code == expected_status_code
    else:
        redirect_response = await ac.get(f"/api/short-links/{slug}")
        assert redirect_response.status_code == expected_status_code
        assert redirect_response.headers["location"] == long_url


async def test_create_short_link_API(ac: AsyncClient):
    response = await ac.post(
        "/api/short-links", json={"long_url": "https://www.example.com/"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "slug" in data
    assert len(data["slug"]) == 6
