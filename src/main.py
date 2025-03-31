from fastapi import Depends
from src.auth.auth import auth_backend
from src.auth.manager import fastapi_users, current_active_user
from src.auth.schemas import UserCreate, UserRead
from src.shorturl.router import router as shortlink_router
from src.tasks.router import router as tasks_router
from src.database import User
from src.app import app

import uvicorn

# Роутеры
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(shortlink_router)
app.include_router(tasks_router)


@app.get("/protected-route")
def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, {user.email}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", log_level="info")
