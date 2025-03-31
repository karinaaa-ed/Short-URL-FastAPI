import smtplib
from email.message import EmailMessage
from celery import Celery
from src.config import SMTP_PASSWORD, SMTP_USER, DEFAULT_UNUSED_LINK_DAYS
from src.database import async_session_maker, Link
from datetime import datetime, timedelta
from sqlalchemy import select


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


celery = Celery(
    'tasks',
    broker='redis://redis_app:5370/0'
)

def get_template_email(username: str):
    email = EmailMessage()
    email['Subject'] = 'Привет'
    email['From'] = SMTP_USER
    email['To'] = SMTP_USER
    email.set_content(
        '<div>'
        f'<h1 style="color: red;">Здравствуйте, {username}</h1>'
        '</div>',
        subtype='html'
    )
    return email


@celery.task(default_retry_delay=5, max_retries=3)
def send_email(username: str):
    email = get_template_email(username)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        print(server.login(SMTP_USER, SMTP_PASSWORD))
        try:
            server.send_message(email)
        except:
            send_email.retry()


def sync_cleanup_expired_links():
    """Синхронная обертка для асинхронной очистки ссылок"""
    import asyncio
    return asyncio.get_event_loop().run_until_complete(async_cleanup_expired_links())

async def async_cleanup_expired_links():
    """Асинхронная реализация очистки просроченных ссылок"""
    async with async_session_maker() as db:
        try:
            # Получаем просроченные ссылки
            expired_links = await db.execute(
                select(Link).where(
                    (Link.expires_at <= datetime.now()) |
                    (
                        (Link.last_clicked_at <= datetime.now() - timedelta(days=DEFAULT_UNUSED_LINK_DAYS)) &
                        (Link.clicks == 0)
                    )
                )
            )
            expired_links = expired_links.scalars().all()

            # Удаляем найденные ссылки
            for link in expired_links:
                await db.delete(link)

            await db.commit()
            return f"Deleted {len(expired_links)} expired/unused links"
        except Exception as e:
            await db.rollback()
            raise e

@celery.task
def cleanup_expired_links():
    """Celery задача для очистки просроченных ссылок"""
    return sync_cleanup_expired_links()
