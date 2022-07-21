from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.schemas import UserCreate, UserModel
from src.services import UserService, get_user_service

router = APIRouter()


@router.post(
    path="/",
    response_model=UserModel,
    summary="Создать аккаунт",
    tags=["users"],
)
def user_create(
    user: UserCreate, user_service: UserService = Depends(get_user_service),
) -> UserModel:
    user: dict = user_service.create_user(user=user)
    if user == dict():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="username already in use or email already in use")
    return UserModel(**user)
