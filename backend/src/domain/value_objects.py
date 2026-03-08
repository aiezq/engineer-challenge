import re
from dataclasses import dataclass
from .exceptions import InvalidEmailError, InvalidPasswordError

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.value):
            raise InvalidEmailError(f"Invalid email address: {self.value}")


@dataclass(frozen=True)
class RawPassword:
    value: str

    def __post_init__(self):
        if len(self.value) < 8:
            raise InvalidPasswordError("Password must be at least 8 characters long")
        # Can add more rules: uppercase, numbers, etc.


@dataclass(frozen=True)
class HashedPassword:
    value: str
