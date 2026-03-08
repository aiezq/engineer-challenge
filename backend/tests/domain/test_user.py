import unittest
from src.domain.user import User
from src.domain.value_objects import Email, RawPassword, HashedPassword
from src.domain.exceptions import InvalidEmailError, InvalidPasswordError, InvalidResetTokenError


class UserDomainTests(unittest.TestCase):
    def test_valid_email_creation_normalizes_case_and_whitespace(self) -> None:
        email = Email("  Test@Example.com ")
        self.assertEqual(email.value, "test@example.com")

    def test_invalid_email_raises_error(self) -> None:
        with self.assertRaises(InvalidEmailError):
            Email("invalid-email")
        with self.assertRaises(InvalidEmailError):
            Email("user@@example.com")
        with self.assertRaises(InvalidEmailError):
            Email("user@example")

    def test_password_policy_validation(self) -> None:
        with self.assertRaises(InvalidPasswordError):
            RawPassword("short")
        with self.assertRaises(InvalidPasswordError):
            RawPassword("lowercaseonly1")
        with self.assertRaises(InvalidPasswordError):
            RawPassword("UPPERCASEONLY1")
        with self.assertRaises(InvalidPasswordError):
            RawPassword("NoDigitsPassword")
        with self.assertRaises(InvalidPasswordError):
            RawPassword(" ValidPassword1")
        with self.assertRaises(InvalidPasswordError):
            RawPassword("A" * 73 + "1a")

        pwd = RawPassword("ValidPassword1")
        self.assertEqual(pwd.value, "ValidPassword1")

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

        user.request_password_reset("hashed-reset-token", expires_in_minutes=15)
        self.assertEqual(user.reset_token_hash, "hashed-reset-token")
        self.assertIsNotNone(user.reset_token_expires_at)

        new_hash = HashedPassword("new_hash")
        user.reset_password(new_hash, "hashed-reset-token")

        self.assertEqual(user.password_hash.value, "new_hash")
        self.assertIsNone(user.reset_token_hash)
        self.assertIsNone(user.reset_token_expires_at)

    def test_password_reset_invalid_token(self) -> None:
        user = User.create(Email("test@example.com"), HashedPassword("hash"))
        user.request_password_reset("valid-token-hash")

        with self.assertRaises(InvalidResetTokenError):
            user.reset_password(HashedPassword("new"), "wrong-token")
