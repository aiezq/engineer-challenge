import pytest
from src.domain.exceptions import InvalidCredentialsError
from src.domain.user import User
from src.domain.value_objects import Email, HashedPassword
from src.infrastructure.auth.token_service import JwtTokenService


def make_user() -> User:
    return User.create(
        email=Email("user@example.com"),
        password_hash=HashedPassword("hashed-password"),
    )


def test_generate_and_decode_token_roundtrip():
    service = JwtTokenService(secret_key="test-secret")
    user = make_user()

    token = service.generate_token(user)
    payload = service.decode_token(token)

    assert payload["sub"] == str(user.id)
    assert payload["email"] == user.email.value


def test_decode_token_rejects_invalid_value():
    service = JwtTokenService(secret_key="test-secret")

    with pytest.raises(InvalidCredentialsError):
        service.decode_token("not-a-valid-jwt")
