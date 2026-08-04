from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

senha = "1234567"
print(pwd_context.hash(senha))