import re
from dataclasses import dataclass
from .exceptions import InvalidEmailError, InvalidPasswordError

EMAIL_PATTERN = re.compile(r"^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        local_part, at, domain_part = normalized.partition("@")
        if (
            not normalized
            or at != "@"
            or normalized.count("@") != 1
            or not local_part
            or not domain_part
            or domain_part.startswith(".")
            or domain_part.endswith(".")
            or ".." in normalized
            or "." not in domain_part
            or not EMAIL_PATTERN.match(normalized)
        ):
            raise InvalidEmailError(f"Invalid email address: {self.value}")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True)
class RawPassword:
    value: str

    def __post_init__(self) -> None:
        if self.value != self.value.strip():
            raise InvalidPasswordError("Password must not start or end with whitespace")
        if len(self.value) < 12:
            raise InvalidPasswordError("Password must be at least 12 characters long")
        if len(self.value) > 72:
            raise InvalidPasswordError("Password must not be longer than 72 characters")
        if not re.search(r"[a-z]", self.value):
            raise InvalidPasswordError("Password must include a lowercase letter")
        if not re.search(r"[A-Z]", self.value):
            raise InvalidPasswordError("Password must include an uppercase letter")
        if not re.search(r"\d", self.value):
            raise InvalidPasswordError("Password must include a digit")


@dataclass(frozen=True)
class HashedPassword:
    value: str
