import unittest
from src.domain.exceptions import InvalidCredentialsError
from src.domain.user import User
from src.domain.value_objects import Email, HashedPassword
from src.infrastructure.auth.token_service import JwtTokenService


def make_user() -> User:
    return User.create(
        email=Email("user@example.com"),
        password_hash=HashedPassword("hashed-password"),
    )


class TokenServiceTests(unittest.TestCase):
    def test_generate_and_decode_token_roundtrip(self) -> None:
        service = JwtTokenService(secret_key="test-secret-key-with-32-bytes!!!")
        user = make_user()

        token = service.generate_token(user)
        payload = service.decode_token(token)

        self.assertEqual(payload.get("sub"), str(user.id))
        self.assertEqual(payload.get("email"), user.email.value)

    def test_decode_token_rejects_invalid_value(self) -> None:
        service = JwtTokenService(secret_key="test-secret-key-with-32-bytes!!!")

        with self.assertRaises(InvalidCredentialsError):
            service.decode_token("not-a-valid-jwt")

    def test_hash_reset_token_is_deterministic_and_not_raw(self) -> None:
        service = JwtTokenService(secret_key="test-secret-key-with-32-bytes!!!")

        hashed_token = service.hash_reset_token("plain-reset-token")

        self.assertEqual(hashed_token, service.hash_reset_token("plain-reset-token"))
        self.assertNotEqual(hashed_token, "plain-reset-token")
