from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from src.auth.manager import current_active_user
from src.tasks.tasks import cleanup_expired_links, send_email
from src.database import User

router = APIRouter(prefix="/report", tags=["report"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/jwt/login")


@router.get("/send")
def send_email_handler():
    try:
        send_email.apply_async(args=['User'])
    except Exception as e:
        return {
            "status": 503,
            "details": str(e),
        }

    return {
        "status": 200,
        "details": "All ok"
    }


@router.post("/cleanup-links")
async def trigger_cleanup_links(
        token: str = Depends(oauth2_scheme),
        user: User = Depends(current_active_user),
):
    """Очистка просроченных ссылок"""
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can trigger this task"
        )

    cleanup_expired_links.delay()
    return {"message": "Cleanup task started"}