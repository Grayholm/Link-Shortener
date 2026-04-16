from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.exceptions import LinkNotFoundError
from src.service import LinkShortenerService


@patch("src.service.LinksRepository")
async def test_create_short_link(mock_repo_class):
    mock_repo_instance = AsyncMock()
    mock_repo_class.return_value = mock_repo_instance

    mock_session = AsyncMock()
    service = LinkShortenerService(mock_session)

    service.generate_short_link = Mock(return_value="abc123")

    result = await service.create_short_link("https://www.example.com")

    assert result == "abc123"

    mock_repo_instance.add_link.assert_called_once_with(
        "abc123",
        "https://www.example.com"
    )

@pytest.mark.parametrize("slug, long_url, should_raise", [
    ("abc123", "https://www.example.com", False),
    ("def456", "https://www.anotherexample.com", False),
    ("ghi789gd", None, True)
])
async def test_redirect_to_url(slug, long_url, should_raise):
    mock_repo_instance = AsyncMock()

    mock_repo_instance.get_link.return_value = long_url

    mock_session = AsyncMock()

    with patch("src.service.LinksRepository", return_value=mock_repo_instance):
        service = LinkShortenerService(mock_session)

        if should_raise:
            with pytest.raises(LinkNotFoundError):
                await service.redirect_to_url(slug)
        else:
            response = await service.redirect_to_url(slug)  

    if not should_raise:
        assert response.status_code == 307
        assert response.headers["location"] == long_url

    assert mock_repo_instance.get_link.call_count == 1
    mock_repo_instance.get_link.assert_called_with(slug)

