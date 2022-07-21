from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.schemas import UserLogin, Logout, Mes
from src.services import UserService, get_user_service

router = APIRouter()


@router.post(
    path="/",
    response_model=Mes,
    summary="Выход из профиля",
    tags=["users"],
)
def user_login(
    logout: Logout, user_service: UserService = Depends(get_user_service),
) -> Mes:
    mes: dict = user_service.logout_user(logout)
    if mes == dict():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found or access token")
    return Mes(**mes)