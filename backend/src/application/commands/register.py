from dataclasses import dataclass
from src.domain.user import User
from src.domain.value_objects import Email, RawPassword, HashedPassword
from src.domain.exceptions import UserAlreadyExistsError
from src.application.ports import UserRepository, PasswordHasher

@dataclass
class RegisterUserCommand:
    email: str
    password: str

class RegisterUserHandler:
    def __init__(self, user_repo: UserRepository, password_hasher: PasswordHasher):
        self._user_repo = user_repo
        self._password_hasher = password_hasher

    async def handle(self, command: RegisterUserCommand) -> User:
        email = Email(command.email)
        raw_password = RawPassword(command.password)
        
        existing_user = await self._user_repo.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError("User with this email already exists")
            
        hashed_pwd = HashedPassword(self._password_hasher.hash_password(raw_password.value))
        user = User.create(email=email, password_hash=hashed_pwd)
        
        await self._user_repo.save(user)
        return user
