from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.exceptions import LinkAlreadyExistsError, LinkNotFoundError
from src.service import LinkShortenerService


@pytest.mark.parametrize("slug, long_url, should_raise", [
    ("abc123", "https://www.example.com", False),
    ("def456", None, True),
])
@patch("src.service.LinksRepository")
async def test_create_short_link(mock_repo_class, slug, long_url, should_raise):
    mock_repo_instance = AsyncMock()
    mock_repo_class.return_value = mock_repo_instance

    mock_session = AsyncMock()
    service = LinkShortenerService(mock_session)

    if should_raise:
        service.generate_short_link = AsyncMock(side_effect=LinkAlreadyExistsError)
        with pytest.raises(LinkAlreadyExistsError):
            await service.create_short_link(long_url)
        
        assert mock_repo_instance.add_link.call_count == 0
    else:
        service.generate_short_link = AsyncMock(return_value=slug)
        result = await service.create_short_link(long_url)

        assert result == slug

        mock_repo_instance.add_link.assert_called_once_with(
            slug,
            long_url
        )

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

