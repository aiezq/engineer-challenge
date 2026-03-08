import pytest
from src.domain.user import User
from src.domain.value_objects import Email, RawPassword, HashedPassword
from src.domain.exceptions import InvalidEmailError, InvalidPasswordError, InvalidResetTokenError

def test_valid_email_creation():
    email = Email("test@example.com")
    assert email.value == "test@example.com"

def test_invalid_email_raises_error():
    with pytest.raises(InvalidEmailError):
        Email("invalid-email")

def test_password_length_validation():
    with pytest.raises(InvalidPasswordError):
        RawPassword("short")
        
    pwd = RawPassword("longenough")
    assert pwd.value == "longenough"

def test_user_creation():
    email = Email("user@example.com")
    hashed_pwd = HashedPassword("hashed_value")
    
    user = User.create(email=email, password_hash=hashed_pwd)
    
    assert user.email.value == "user@example.com"
    assert user.is_active is True
    assert user.id is not None

def test_password_reset_flow():
    email = Email("user@example.com")
    hashed_pwd = HashedPassword("old_hash")
    user = User.create(email=email, password_hash=hashed_pwd)
    
    # Request reset
    user.request_password_reset("secret-token", expires_in_minutes=15)
    assert user.reset_token == "secret-token"
    assert user.reset_token_expires_at is not None
    
    # Reset with valid token
    new_hash = HashedPassword("new_hash")
    user.reset_password(new_hash, "secret-token")
    
    assert user.password_hash.value == "new_hash"
    assert user.reset_token is None
    assert user.reset_token_expires_at is None

def test_password_reset_invalid_token():
    user = User.create(Email("test@example.com"), HashedPassword("hash"))
    user.request_password_reset("valid-token")
    
    with pytest.raises(InvalidResetTokenError):
        user.reset_password(HashedPassword("new"), "wrong-token")
