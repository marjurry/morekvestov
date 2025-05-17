from passlib.context import CryptContext
from sqlalchemy import Boolean
from app.models import pwd_context

'''pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")'''

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)