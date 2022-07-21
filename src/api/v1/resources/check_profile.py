from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.schemas import UserWithToken, UserModel, Token, CheckProfile, ChangeProfile
from src.services import UserService, get_user_service

router = APIRouter()


@router.post(
    path="/",
    response_model=UserModel,
    summary="Просмотр своего профиля",
    tags=["users"],
)
def user_profile(
    user: CheckProfile, user_service: UserService = Depends(get_user_service),
) -> UserModel:
    profile: dict = user_service.check_profile(user)
    if profile == dict():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found or bad access token")
    return UserModel(**profile)


@router.put(
    path="/",
    response_model=UserWithToken,
    summary="Изменение своего профиля",
    tags=["users"],
)
def change_profile(
    change: ChangeProfile, user_service: UserService = Depends(get_user_service),
) -> UserWithToken:
    new_profile: dict = user_service.change_profile(change)
    if new_profile == dict():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found or bad access token or username"
                                                                     "already in use or email already in use")
    return UserWithToken(**new_profile)
