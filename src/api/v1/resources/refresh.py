from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.schemas import RefreshToken, Token
from src.services import UserService, get_user_service


router = APIRouter()


@router.post(
    path="/",
    response_model=Token,
    summary="Обновление токена",
    tags=["users"],
)
def user_refresh(
    refresh_token: RefreshToken, user_service: UserService = Depends(get_user_service),
) -> Token:
    token: dict = user_service.refresh(refresh_token)
    if token == dict():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Bad refresh token or id not found")
    return Token(**token)
