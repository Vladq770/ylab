from jwt import encode
from functools import lru_cache
from typing import Optional
from datetime import datetime, timedelta
from fastapi import Depends
from sqlmodel import Session
from src.core.config import JWT_SECRET_KEY, JWT_ALGORITHM
from src.api.v1.schemas import UserCreate, UserModel, UserLogin, Token, RefreshToken, CheckProfile, ChangeProfile,\
    UserWithToken, Logout, Mes
from src.db import AbstractCache, get_cache, get_session
from src.models import User
from src.services import ServiceMixin

__all__ = ("UserService", "get_user_service")


class UserService(ServiceMixin):
   
    def create_user(self, user: UserCreate) -> dict:
        users = self.session.query(User).order_by(User.created_at).all()
        for i in users:
            if i.username == user.username or i.email == user.email:
                return dict()
        new_user = User(username=user.username, password=user.password, email=user.email)
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user.dict()

    def login_user(self, user: UserLogin) -> dict:
        users = self.session.query(User).order_by(User.created_at).all()
        for i in users:
            if i.username == user.username and i.password == user.password:
                time = int(datetime.utcnow().timestamp())
                access_token = encode({"username": i.username, "time": time}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
                refresh_token = encode({"id": i.id, "time": time}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
                token = Token()
                token.accessToken = access_token
                token.refreshToken = refresh_token
                i.last_login = time
                self.session.add(i)
                self.session.commit()
                token.expires_in = time + 300    # 5 минут для access token
                i.expires_in = time + 2592000    # 30 дней для refresh token
                self.session.add(i)
                self.session.commit()
                return token.dict()
        return dict()

    def refresh(self, refresh_token: RefreshToken) -> dict:
        user = self.session.query(User).get(refresh_token.id)
        if user is None or user.expires_in < int(datetime.utcnow().timestamp()):
            return dict()
        if refresh_token.refreshToken != encode({"id": user.id, "time": user.last_login}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM):
            return dict()
        time = int(datetime.utcnow().timestamp())
        access_token = encode({"username": user.username, "time": time}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        refresh_token = encode({"id": user.id, "time": time}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        token = Token()
        token.accessToken = access_token
        token.refreshToken = refresh_token
        user.last_login = time
        self.session.add(user)
        self.session.commit()
        token.expires_in = time + 300  # 5 минут для access token
        user.expires_in = time + 2592000  # 30 дней для refresh token
        self.session.add(user)
        self.session.commit()
        return token.dict()

    def check_profile(self, user: CheckProfile) -> dict:
        profile = self.session.query(User).get(user.id)
        if profile is None or profile.last_login + 300 < int(datetime.utcnow().timestamp()):  # +300: истек ли access token
            return dict()
        if user.accessToken != encode({"username": profile.username, "time": profile.last_login}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM):
            return dict()
        return profile.dict()

    def change_profile(self, change: ChangeProfile) -> dict:
        profile = self.session.query(User).get(change.id)
        if profile is None or profile.last_login + 300 < int(datetime.utcnow().timestamp()):  # +300: истек ли access token
            return dict()
        if change.accessToken != encode({"username": profile.username, "time": profile.last_login}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM):
            return dict()
        users = self.session.query(User).order_by(User.created_at).all()
        if change.new_email != "":
            for i in users:
                if i.email == change.new_email:
                    return dict()
            profile.email = change.new_email
            self.session.add(profile)
            self.session.commit()
        if change.new_username != "":
            for i in users:
                if i.username == change.new_username:
                    return dict()
            profile.username = change.new_username
            self.session.add(profile)
            self.session.commit()
        if change.new_password != "":
            profile.password = change.new_password
            self.session.add(profile)
            self.session.commit()
        time = int(datetime.utcnow().timestamp())
        profile.last_login = time
        self.session.add(profile)
        self.session.commit()
        profile.expires_in = time + 2592000  # 30 дней для refresh token
        self.session.add(profile)
        self.session.commit()
        user_with_token = UserWithToken(id=profile.id, created_at=profile.created_at, role=profile.role,
                                        is_superuser=profile.is_superuser, is_active=profile.is_active,
                                        is_totp_enabled=profile.is_totp_enabled, email=profile.email,
                                        username=profile.username)
        user_with_token.accessToken = encode({"username": profile.username, "time": time}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        user_with_token.refreshToken = encode({"id": profile.id, "time": time}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        user_with_token.expires_in = time + 300  # 5 минут для access token
        return user_with_token.dict()

    def logout_user(self, logout: Logout) -> dict:
        profile = self.session.query(User).get(logout.id)
        if profile is None or profile.last_login + 300 < int(datetime.utcnow().timestamp()):  # +300: истек ли access token
            return dict()
        if logout.accessToken != encode({"username": profile.username, "time": profile.last_login}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM):
            return dict()
        profile.last_login = 0
        self.session.add(profile)
        self.session.commit()
        mes = Mes(mes="You have been logget out")
        return mes.dict()
# get_post_service — это провайдер PostService. Синглтон
@lru_cache()
def get_user_service(
    cache: AbstractCache = Depends(get_cache),
    session: Session = Depends(get_session),
) -> UserService:
    return UserService(cache=cache, session=session)
