import uuid
from datetime import timedelta, datetime

import jwt
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from warmhouse.lib.models import Token
from warmhouse.ms_auth.utils import oauth2_scheme
from warmhouse.ms_auth.settings import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from warmhouse.ms_auth.depends.dependencies import get_db
from warmhouse.ms_auth.services.auth import get_current_user, create_access_token, get_user_by_email, authenticate_user
from warmhouse.ms_auth.utils import get_password_hash

router = APIRouter(prefix="/auth")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), pool=Depends(get_db),):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]},
        expires_delta=access_token_expires
    )

    # Сохраняем сессию
    async with pool.acquire() as conn:
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + access_token_expires
        await conn.execute(
            "INSERT INTO user_sessions (id, user_id, token, expires_at) VALUES ($1, $2, $3, $4)",
            session_id, user["id"], access_token, expires_at
        )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user["id"]
    )


@router.post("/register")
async def register_user(user_data: dict, pool=Depends(get_db),):
    email = user_data.get("email")
    username = user_data.get("username")
    password = user_data.get("password")
    full_name = user_data.get("full_name")

    # Проверка существования пользователя
    existing_user = await get_user_by_email(email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(password)

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (id, email, username, full_name, hashed_password)
            VALUES ($1, $2, $3, $4, $5)
        """, user_id, email, username, full_name, hashed_password)

    # Создание токена
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id, "email": email},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user_id
    )


@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "is_active": current_user["is_active"]
    }


@router.post("/internal/validate")
async def validate_token(request: dict, pool=Depends(get_db),):
    """Внутренний эндпоинт для валидации токена другими сервисами"""
    token = request.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token required")

    try:
        payload = jwt.JWT().decode(message=token, key=SECRET_KEY, algorithms={ALGORITHM})
        user_id = payload.get("sub")

        async with pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE id = $1 AND is_active = TRUE", user_id)
            if not user:
                raise HTTPException(status_code=401, detail="User not found or inactive")

            session = await conn.fetchrow(
                "SELECT * FROM user_sessions WHERE token = $1 AND is_active = TRUE AND expires_at > NOW()",
                token
            )
            if not session:
                raise HTTPException(status_code=401, detail="Invalid or expired session")

        return {
            "valid": True,
            "user_id": user_id,
            "email": payload.get("email"),
            "expires_at": payload.get("exp")
        }
    except:
        return {"valid": False, "error": "Invalid token"}


@router.post("/logout")
async def logout(pool=Depends(get_db), _: dict = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    """Выход пользователя"""
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE user_sessions SET is_active = FALSE WHERE token = $1",
            token
        )
    return {"message": "Successfully logged out"}