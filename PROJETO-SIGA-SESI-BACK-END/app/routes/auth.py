from fastapi import APIRouter, HTTPException, Request, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from app.config.database import SessionLocal
from app.models.user import User
from app.models.matricula import Matricula
from app.schemas.user_schema import LoginSchema
from app.config.security import (
    create_access_token,
    create_refresh_token,
    verify_token
)

router = APIRouter()

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# 🔒 CONTROLE DE TENTATIVAS (em memória)
tentativas_por_ip = {}

LIMITE_TENTATIVAS = 10
BLOQUEIO_HORAS = 1


# 🔐 SENHA
def verify_password(plain, hashed):
    try:
        return pwd_context.verify(plain, hashed)
    except UnknownHashError:
        return False


# 🔒 REGISTRAR TENTATIVA
def registrar_tentativa(ip):
    registro = tentativas_por_ip.get(ip)

    if not registro:
        tentativas_por_ip[ip] = {
            "tentativas": 1,
            "bloqueado_ate": None
        }
        return

    registro["tentativas"] += 1

    if registro["tentativas"] >= LIMITE_TENTATIVAS:
        registro["bloqueado_ate"] = datetime.utcnow() + timedelta(hours=BLOQUEIO_HORAS)


# 🚫 VERIFICAR BLOQUEIO
def verificar_bloqueio(ip):
    registro = tentativas_por_ip.get(ip)

    if registro:
        if registro["bloqueado_ate"] and datetime.utcnow() < registro["bloqueado_ate"]:
            raise HTTPException(
                status_code=429,
                detail="Muitas tentativas. Tente novamente mais tarde"
            )


# 🔑 LOGIN
@router.post("/login")
def login(data: LoginSchema, request: Request):

    ip = request.client.host

    # 🔒 verificar bloqueio
    verificar_bloqueio(ip)

    db: Session = SessionLocal()

    try:
        user = None

        # 🔎 Buscar usuário
        if data.emailUser:
            user = db.query(User).filter(User.emailUser == data.emailUser).first()

        elif data.cpfUser:
            user = db.query(User).filter(User.cpfUser == data.cpfUser).first()

        elif data.rm:
            matricula = db.query(Matricula).filter(
                Matricula.rm == data.rm,
                Matricula.idEscola == data.escolaId,
                Matricula.ativo == True
            ).first()

            if not matricula:
                registrar_tentativa(ip)
                raise HTTPException(status_code=401, detail="Usuário ou senha incorreta")

            user = db.query(User).filter(User.idUser == matricula.idUser).first()

        if not user:
            registrar_tentativa(ip)
            raise HTTPException(status_code=401, detail="Usuário ou senha incorreta")

        # 🔒 validar tipo
        if user.tipoUser != data.tipoUser.upper():
            registrar_tentativa(ip)
            raise HTTPException(status_code=401, detail="Usuário ou senha incorreta")

        # 🔒 validar escola
        matricula = db.query(Matricula).filter(
            Matricula.idUser == user.idUser,
            Matricula.idEscola == data.escolaId,
            Matricula.ativo == True
        ).first()

        if not matricula:
            registrar_tentativa(ip)
            raise HTTPException(status_code=401, detail="Usuário ou senha incorreta")

        # 🔐 validar senha
        if not verify_password(data.password, user.password):
            registrar_tentativa(ip)
            raise HTTPException(status_code=401, detail="Usuário ou senha incorreta")

        # 🔑 gerar tokens
        access_token = create_access_token({
            "sub": str(user.idUser),
            "tipoUser": user.tipoUser
        })

        refresh_token = create_refresh_token({
            "sub": str(user.idUser)
        })

        # ✅ RESETAR TENTATIVAS
        tentativas_por_ip[ip] = {
            "tentativas": 0,
            "bloqueado_ate": None
        }

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "tipoUser": user.tipoUser
        }

    finally:
        db.close()


# 🔄 REFRESH TOKEN
@router.post("/refresh")
def refresh_token(refresh_token: str = Body(...)):
    payload = verify_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    new_access = create_access_token({
        "sub": payload["sub"]
    })

    return {
        "access_token": new_access
    
       }
