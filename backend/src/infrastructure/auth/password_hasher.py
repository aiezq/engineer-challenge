from passlib.context import CryptContext
from src.application.ports import PasswordHasher

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class BcryptPasswordHasher(PasswordHasher):
    def hash_password(self, plain_password: str) -> str:
        return pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
