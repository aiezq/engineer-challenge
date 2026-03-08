import strawberry
from typing import Optional

@strawberry.type
class UserType:
    id: str
    email: str
    is_active: bool
    created_at: str

@strawberry.type
class AuthResultType:
    access_token: str
    user_id: str

@strawberry.type
class PasswordResetRequestResultType:
    ok: bool
    delivery_mode: str
    reset_url_preview: Optional[str]

@strawberry.input
class RegisterUserInput:
    email: str
    password: str

@strawberry.input
class AuthenticateInput:
    email: str
    password: str

@strawberry.input
class RequestResetInput:
    email: str

@strawberry.input
class ResetPasswordInput:
    token: str
    new_password: str
