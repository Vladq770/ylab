from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.schemas import UserLogin, UserModel, Token
from src.services import UserService, get_user_service

router = APIRouter()


@router.post(
    path="/",
    response_model=Token,
    summary="Вход в профиль",
    tags=["users"],
)
def user_login(
    user: UserLogin, user_service: UserService = Depends(get_user_service),
) -> Token:
    token: dict = user_service.login_user(user)
    if token == dict():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found or bad password")
    return Token(**token)
