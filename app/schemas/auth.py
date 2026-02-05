from typing import List, Optional

from .common import APIModel


class LoginRequest(APIModel):
    identity: str
    password: str


class RegisterRequest(APIModel):
    identity: str
    password: str
    display_name: str


class AuthUser(APIModel):
    id: str
    displayName: str
    identity: str
    roles: Optional[List[str]] = None


class AuthResult(APIModel):
    access_token: str
    user: AuthUser
