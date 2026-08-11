from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

senha = "123456"
print(pwd_context.hash(senha))