import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from src.tasks.tasks import send_email, async_cleanup_expired_links


@patch('smtplib.SMTP_SSL')
def test_send_email_success(mock_smtp):
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    send_email("testuser")

    mock_server.login.assert_called_once()
    mock_server.send_message.assert_called_once()


@patch('smtplib.SMTP_SSL')
def test_send_email_retry(mock_smtp):
    mock_server = MagicMock()
    mock_server.send_message.side_effect = Exception("SMTP error")
    mock_smtp.return_value = mock_server

    try:
        send_email("testuser")
    except Exception:
        pass

    assert mock_server.send_message.call_count == 3


@pytest.mark.asyncio
async def test_cleanup_expired_links():
    # Мок для результата запроса
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    # Мок для сессии с execute
    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    # Мок для асинхронного контекстного менеджера
    mock_session_context = AsyncMock()
    mock_session_context.__aenter__.return_value = mock_session

    # Мок для async_session_maker
    mock_session_maker = MagicMock()
    mock_session_maker.return_value = mock_session_context

    with patch('src.tasks.tasks.async_session_maker', new=mock_session_maker):
        with patch('src.tasks.tasks.DEFAULT_UNUSED_LINK_DAYS', 30):
            with patch('src.tasks.tasks.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2023, 1, 1)

                # Вызов тестируемой функции
                result = await async_cleanup_expired_links()

                # Проверка результата
                assert "Deleted 0 expired/unused links" in result

                # Проверка вызовов
                mock_session.execute.assert_called_once()
                mock_session.commit.assert_called_once()