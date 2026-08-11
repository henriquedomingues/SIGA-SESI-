from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import or_
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.security import verify_password
from app.database.connection import SessionLocal
from app.models.user import User


ADMIN_ROLE = "ADMIN"
ADMIN_SESSION_KEY = "admin_user_id"


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool | RedirectResponse:
        form = await request.form()
        username = str(form.get("username", "")).strip()
        password = str(form.get("password", ""))

        if not username or not password:
            return False

        db = SessionLocal()
        try:
            user = (
                db.query(User)
                .filter(
                    or_(
                        User.emailUser == username,
                        User.cpfUser == username,
                    )
                )
                .first()
            )

            if not user or user.tipoUser != ADMIN_ROLE or not user.password:
                return False

            if not verify_password(password, user.password):
                return False

            request.session.update(
                {
                    ADMIN_SESSION_KEY: user.idUser,
                    "admin_user_name": user.nomeUser,
                    "admin_user_role": user.tipoUser,
                }
            )
            return True
        finally:
            db.close()

    async def logout(self, request: Request) -> bool | RedirectResponse:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool | RedirectResponse:
        admin_user_id = request.session.get(ADMIN_SESSION_KEY)
        admin_user_role = request.session.get("admin_user_role")

        return bool(admin_user_id and admin_user_role == ADMIN_ROLE)
