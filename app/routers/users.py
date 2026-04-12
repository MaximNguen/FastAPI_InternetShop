from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
import jwt

from app.models.users import User as UserModel
from app.schemas import User as UserSchema, UserCreate, RefreshTokenRequest
from app.db_depends import get_async_db
from app.auth import create_refresh_token, hash_password, verify_password, create_access_token
from app.config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, db: AsyncSession = Depends(get_async_db)):
    result = await db.scalar(select(UserModel).where(UserModel.email == user_create.email))
    if result:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким email уже существует")
    db_user = UserModel(
        email=user_create.email,
        hashed_password=hash_password(user_create.password),
        role=user_create.role
    )
    db.add(db_user)
    await db.commit()
    return db_user

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
    result = await db.scalars(
        select(UserModel).where(UserModel.email == form_data.username, UserModel.is_active == True))
    user = result.first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh-token")
async def refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_async_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        token_type: str | None = payload.get("token_type")

        if not isinstance(user_id, int) or token_type != "refresh":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await db.scalar(select(UserModel).where(UserModel.id == user_id, UserModel.is_active == True))
    if user is None:
        raise credentials_exception

    new_refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {"refresh_token": new_refresh_token, "token_type": "bearer"}

@router.post("/access-token")
async def access_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_async_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        token_type: str | None = payload.get("token_type")

        if not isinstance(user_id, int) or token_type != "refresh":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await db.scalar(select(UserModel).where(UserModel.id == user_id, UserModel.is_active == True))
    if user is None:
        raise credentials_exception
                        
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
    