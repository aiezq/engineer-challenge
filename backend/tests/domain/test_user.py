import unittest
from src.domain.user import User
from src.domain.value_objects import Email, RawPassword, HashedPassword
from src.domain.exceptions import InvalidEmailError, InvalidPasswordError, InvalidResetTokenError


class UserDomainTests(unittest.TestCase):
    def test_valid_email_creation(self) -> None:
        email = Email("test@example.com")
        self.assertEqual(email.value, "test@example.com")

    def test_invalid_email_raises_error(self) -> None:
        with self.assertRaises(InvalidEmailError):
            Email("invalid-email")

    def test_password_length_validation(self) -> None:
        with self.assertRaises(InvalidPasswordError):
            RawPassword("short")

        pwd = RawPassword("longenough")
        self.assertEqual(pwd.value, "longenough")

    def test_user_creation(self) -> None:
        email = Email("user@example.com")
        hashed_pwd = HashedPassword("hashed_value")

        user = User.create(email=email, password_hash=hashed_pwd)

        self.assertEqual(user.email.value, "user@example.com")
        self.assertTrue(user.is_active)
        self.assertIsNotNone(user.id)

    def test_password_reset_flow(self) -> None:
        email = Email("user@example.com")
        hashed_pwd = HashedPassword("old_hash")
        user = User.create(email=email, password_hash=hashed_pwd)

        user.request_password_reset("secret-token", expires_in_minutes=15)
        self.assertEqual(user.reset_token, "secret-token")
        self.assertIsNotNone(user.reset_token_expires_at)

        new_hash = HashedPassword("new_hash")
        user.reset_password(new_hash, "secret-token")

        self.assertEqual(user.password_hash.value, "new_hash")
        self.assertIsNone(user.reset_token)
        self.assertIsNone(user.reset_token_expires_at)

    def test_password_reset_invalid_token(self) -> None:
        user = User.create(Email("test@example.com"), HashedPassword("hash"))
        user.request_password_reset("valid-token")

        with self.assertRaises(InvalidResetTokenError):
            user.reset_password(HashedPassword("new"), "wrong-token")
