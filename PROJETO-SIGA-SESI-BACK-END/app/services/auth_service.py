from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.repositories.matricula_repository import MatriculaRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import LoginSchema
from app.services.login_attempt_service import (
    register_failed_attempt,
    reset_attempts,
    verify_ip_block,
)


INVALID_CREDENTIALS_MESSAGE = "Usuario ou senha incorreta"


class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.matricula_repository = MatriculaRepository(db)

    def login(self, data: LoginSchema, ip_address: str) -> dict:
        verify_ip_block(ip_address)

        user = self._find_user(data)
        if not user:
            self._reject_login(ip_address)

        if user.tipoUser != data.tipoUser.upper():
            self._reject_login(ip_address)

        matricula = self.matricula_repository.get_active_by_user_and_school(
            user.idUser,
            data.escolaId,
        )
        if not matricula:
            self._reject_login(ip_address)

        if not verify_password(data.password, user.password):
            self._reject_login(ip_address)

        reset_attempts(ip_address)

        token = create_access_token(
            {
                "sub": str(user.idUser),
                "tipoUser": user.tipoUser,
            }
        )

        return {
            "token": token,
            "token_type": "Bearer",
        }

    def _find_user(self, data: LoginSchema):
        if data.emailUser:
            return self.user_repository.get_by_email(data.emailUser)

        if data.cpfUser:
            return self.user_repository.get_by_cpf(data.cpfUser)

        if data.rm:
            matricula = self.matricula_repository.get_active_by_rm_and_school(
                data.rm,
                data.escolaId,
            )
            if not matricula:
                return None
            return self.user_repository.get_by_id(matricula.idUser)

        return None

    @staticmethod
    def _reject_login(ip_address: str) -> None:
        register_failed_attempt(ip_address)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS_MESSAGE,
        )
