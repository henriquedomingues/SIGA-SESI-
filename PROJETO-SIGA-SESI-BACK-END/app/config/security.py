from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "SUA_CHAVE_SUPER_SECRETA_AQUI"
ALGORITHM = "HS256"

# --- CONFIGURAÇÃO DE TEMPOS ---
# Para usar minutos/dias depois, basta descomentar estas e comentar as de segundos.

ACCESS_EXPIRE_MINUTES = 30  
#ACCESS_EXPIRE_SECONDS = 2    # Tempo curto para seu teste

REFRESH_EXPIRE_DAYS = 7
#REFRESH_EXPIRE_SECONDS = 2   # Tempo curto para seu teste


# 🔐 ACCESS TOKEN
def create_access_token(data: dict):
    to_encode = data.copy()
    
    # Linha para uso futuro (minutos):
    # expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    
    # Linha para seu teste atual (segundos):
    expire = datetime.utcnow() + timedelta(seconds=ACCESS_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 🔁 REFRESH TOKEN
def create_refresh_token(data: dict):
    to_encode = data.copy()
    
    # Linha para uso futuro (dias):
    # expire = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
    
    # Linha para seu teste atual (segundos):
    expire = datetime.utcnow() + timedelta(seconds=REFRESH_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 🔍 VALIDAR TOKEN
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None