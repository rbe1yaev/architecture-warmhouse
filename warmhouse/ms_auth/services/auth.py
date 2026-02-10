from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import HTTPException, Depends
from starlette import status

from warmhouse.ms_auth.app import SECRET_KEY, ALGORITHM, oauth2_scheme
from warmhouse.ms_auth.depends.dependencies import get_db
from warmhouse.ms_auth.utils import verify_password


async def get_user_by_email(email: str, pool=Depends(get_db)):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
        return row


async def authenticate_user(email: str, password: str):
    user = await get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.JWT().encode(payload=to_encode, key=SECRET_KEY, alg=ALGORITHM)
    return encoded_jwt



async def get_user_by_id(user_id: str, pool=Depends(get_db)):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        return row


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.JWT().decode(message=token, key=SECRET_KEY, algorithms={ALGORITHM})
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except:
        raise credentials_exception

    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user
