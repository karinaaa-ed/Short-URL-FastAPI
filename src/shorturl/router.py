from typing import Union
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi_cache.decorator import cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from sqlalchemy.sql import func
from urllib.parse import unquote

from src.database import get_async_session, User, Link, ExpiredLink
from src.auth.manager import current_active_user
from src.shorturl.schemas import LinkCreate, LinkResponse, LinkCodeUpdate, PublicLinkCreate
from src.utils.short_code import generate_short_code
from src.shorturl.expired_link import ExpiredLinkResponse


router = APIRouter(
    prefix="/links",
    tags=["Links"]
)


@router.post("/shorten", status_code=status.HTTP_201_CREATED, response_model=LinkResponse)
async def create_short_url(
    link_data: Union[LinkCreate, PublicLinkCreate],
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Создание короткой ссылки"""
    # Проверяем, есть ли поле custom_alias в переданных данных
    has_custom_alias = hasattr(link_data, 'custom_alias') and link_data.custom_alias is not None

    # Обработка кастомного алиаса
    if has_custom_alias:
        existing_link = await db.execute(
            select(Link).where(Link.short_code == link_data.custom_alias)
        )
        if existing_link.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom alias already exists"
            )
        short_code = link_data.custom_alias
        is_custom = True
    else:
        short_code = generate_short_code(6)
        is_custom = False

    # Создаем ссылку
    link = Link(
        original_url=str(link_data.original_url),
        short_code=short_code,
        expires_at=link_data.expires_at,
        user_id=user.id,
        is_custom=is_custom,
        project=link_data.project
    )

    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


@router.get("/{short_code}")
@cache(expire=60)
async def redirect_to_original(
    short_code: str,
    db: AsyncSession = Depends(get_async_session),
):
    """Получение оригинального URL по короткой ссылке"""
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalar_one_or_none()

    if not link or not link.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found or expired"
        )

    link.clicks += 1
    link.last_clicked_at = datetime.now(timezone.utc)
    await db.commit()
    return RedirectResponse(url=link.original_url)


@router.get("/{short_code}/stats", response_model=LinkResponse)
@cache(expire=30)
async def get_link_stats(
        short_code: str,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    """Статистика по ссылке (Отображает оригинальный URL, возвращает дату создания, количество переходов, дату последнего использовани)"""
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )

    if link.user_id and link.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this link's stats"
        )

    return link


@router.put("/{short_code}", response_model=LinkResponse)
async def update_link(
        short_code: str,
        new_code: LinkCodeUpdate,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    """Редактирование коротких ссылок"""
    # Находим исходную ссылку
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link with this short code not found"
        )

    # Проверка права доступа
    if link.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this link"
        )

    # Проверка на дубликат
    if link.short_code != new_code.short_code:  # если код действительно меняется
        existing = await db.execute(select(Link).where(Link.short_code == new_code.short_code))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="This short code already exists")

    # Обновление ссылки
    link.short_code = new_code.short_code
    link.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(link)
    return link


@router.delete("/{short_code}")
async def delete_link(
        short_code: str,
        request: Request,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    """Удаление информации по короткой ссылке"""
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )

    if link.user_id and link.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this link"
        )

    await db.delete(link)
    await db.commit()

    await request.app.state.redis.delete(f"shorturl:{short_code}")
    await request.app.state.redis.delete(f"shorturl:{short_code}:stats")

    return {"message": "Link deleted successfully"}


@router.get("/search")
@cache(expire=60)
async def search_links(
        original_url: str,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    """Поиск ссылки по оригинальному URL"""
    decoded_url = unquote(original_url)  # Декодирование URL

    result = await db.execute(
        select(Link).where(
            Link.original_url.ilike(f"%{decoded_url}%"),
            Link.user_id == user.id
        )
    )
    links = result.scalars().all()

    if not links:
        raise HTTPException(
            status_code=404,
            detail="No links found for the provided URL"
        )

    print(f"Found {len(links)} links for URL: {decoded_url}")
    return links if links else []


@router.get("/projects/{project_name}", response_model=list[LinkResponse])
@cache(expire=60)
async def get_project_links(
    project_name: str,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Получение всех ссылок проекта"""
    result = await db.execute(
        select(Link)
        .where(Link.project == project_name)
        .where(Link.user_id == user.id)
    )
    return result.scalars().all()

@router.get("/expired/", response_model=list[ExpiredLinkResponse])
async def get_expired_links(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Получение истории истекших ссылок"""
    result = await db.execute(
        select(ExpiredLink)
        .where(ExpiredLink.user_id == user.id)
    )
    return result.scalars().all()


@router.post("/public/", response_model=LinkResponse)
async def create_public_short_url(
        link_data: PublicLinkCreate,
        db: AsyncSession = Depends(get_async_session),
):
    """Создание короткой ссылки без аутентификации"""
    # Ограничение количества ссылок для анонимов
    existing_links = await db.execute(
        select(func.count()).where(Link.user_id.is_(None))
    )
    if existing_links.scalar() >= 100:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Maximum number of anonymous links reached"
        )

    # Создаем анонимную ссылку
    has_custom_alias = hasattr(link_data, 'custom_alias') and link_data.custom_alias is not None
    if has_custom_alias:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Custom aliases are not allowed for unauthenticated users"
        )

    short_code = generate_short_code(6)

    link = Link(
        original_url=str(link_data.original_url),
        short_code=short_code,
        expires_at=link_data.expires_at,
        user_id=None,
        is_custom=False,
        project=link_data.project
    )

    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link



