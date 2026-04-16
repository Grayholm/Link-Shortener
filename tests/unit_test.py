from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from src.exceptions import LinkAlreadyExistsError, LinkNotFoundError
from src.service import LinkShortenerService, MAX_CREATE_RETRIES


@patch("src.service.LinksRepository")
async def test_create_short_link(mock_repo_class):
    mock_repo_instance = AsyncMock()
    mock_repo_class.return_value = mock_repo_instance

    mock_session = AsyncMock()
    service = LinkShortenerService(mock_session)
    service.generate_short_link = AsyncMock(return_value="abc123")

    result = await service.create_short_link("https://www.example.com")

    assert result == "abc123"
    mock_repo_instance.add_link.assert_called_once_with(
        "abc123",
        "https://www.example.com"
    )

@patch("src.service.LinksRepository")
async def test_create_short_link_retries_on_integrity_error(mock_repo_class):
    mock_repo_instance = AsyncMock()
    mock_repo_instance.add_link.side_effect = [IntegrityError("", "", ""), None]
    mock_repo_class.return_value = mock_repo_instance

    mock_session = AsyncMock()
    service = LinkShortenerService(mock_session)
    service.generate_short_link = AsyncMock(side_effect=["abc123", "def456"])

    result = await service.create_short_link("https://www.example.com")

    assert result == "def456"
    assert mock_repo_instance.add_link.call_count == 2

@patch("src.service.LinksRepository")
async def test_create_short_link_raises_after_retry_limit(mock_repo_class):
    mock_repo_instance = AsyncMock()
    mock_repo_instance.add_link.side_effect = IntegrityError("", "", "")
    mock_repo_class.return_value = mock_repo_instance

    mock_session = AsyncMock()
    service = LinkShortenerService(mock_session)
    service.generate_short_link = AsyncMock(
        side_effect=[f"slug{i}" for i in range(MAX_CREATE_RETRIES)]
    )

    with pytest.raises(LinkAlreadyExistsError):
        await service.create_short_link("https://www.example.com")

    assert mock_repo_instance.add_link.call_count == MAX_CREATE_RETRIES

@pytest.mark.parametrize("slug, long_url, should_raise", [
    ("abc123", "https://www.example.com", False),
    ("def456", "https://www.anotherexample.com", False),
    ("ghi789gd", None, True),
    ("xyz000", None, True),
])
async def test_redirect_to_url(slug, long_url, should_raise):
    mock_repo_instance = AsyncMock()
    mock_session = AsyncMock()
    mock_redis = AsyncMock()

    mock_repo_instance.get_link.return_value = long_url
    mock_redis.get_value.return_value = None

    with patch("src.service.LinksRepository", return_value=mock_repo_instance):
        service = LinkShortenerService(mock_session)
        service.redis = mock_redis

        if should_raise:
            with pytest.raises(LinkNotFoundError):
                await service.redirect_to_url(slug)
        else:
            response = await service.redirect_to_url(slug)  

    if not should_raise:
        assert response == long_url
        mock_redis.set_value.assert_called_once_with(f"redirect:{slug}", long_url, ttl=300)
    else:
        mock_redis.set_value.assert_not_called()

    assert mock_repo_instance.get_link.call_count == 1
    mock_repo_instance.get_link.assert_called_with(slug)

async def test_redirect_to_url_returns_db_value_when_redis_read_fails():
    mock_repo_instance = AsyncMock()
    mock_repo_instance.get_link.return_value = "https://www.example.com"
    mock_session = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get_value.side_effect = RuntimeError("redis down")

    with patch("src.service.LinksRepository", return_value=mock_repo_instance):
        service = LinkShortenerService(mock_session)
        service.redis = mock_redis

        response = await service.redirect_to_url("abc123")

    assert response == "https://www.example.com"
    mock_repo_instance.get_link.assert_called_once_with("abc123")
    mock_redis.set_value.assert_called_once_with(
        "redirect:abc123",
        "https://www.example.com",
        ttl=300,
    )

async def test_redirect_to_url_returns_db_value_when_redis_write_fails():
    mock_repo_instance = AsyncMock()
    mock_repo_instance.get_link.return_value = "https://www.example.com"
    mock_session = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get_value.return_value = None
    mock_redis.set_value.side_effect = RuntimeError("redis down")

    with patch("src.service.LinksRepository", return_value=mock_repo_instance):
        service = LinkShortenerService(mock_session)
        service.redis = mock_redis

        response = await service.redirect_to_url("abc123")

    assert response == "https://www.example.com"
    mock_repo_instance.get_link.assert_called_once_with("abc123")
    mock_redis.set_value.assert_called_once_with(
        "redirect:abc123",
        "https://www.example.com",
        ttl=300,
    )

