class DomainException(Exception):
    """Base class for all domain exceptions."""
    pass

class InvalidEmailError(DomainException):
    pass

class InvalidPasswordError(DomainException):
    pass

class UserAlreadyExistsError(DomainException):
    pass

class InvalidCredentialsError(DomainException):
    pass

class InvalidResetTokenError(DomainException):
    pass
