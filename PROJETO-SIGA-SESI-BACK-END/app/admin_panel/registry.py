from fastapi import FastAPI
from sqladmin import Admin

from app.admin_panel.auth import AdminAuth
from app.admin_panel.views import MatriculaAdmin, UserAdmin
from app.core.config import settings
from app.database.connection import engine


def setup_admin_panel(app: FastAPI) -> Admin:
    authentication_backend = AdminAuth(secret_key=settings.secret_key)

    admin = Admin(
        app=app,
        engine=engine,
        title="SIGA SESI Admin",
        base_url="/admin",
        authentication_backend=authentication_backend,
    )

    admin.add_view(UserAdmin)
    admin.add_view(MatriculaAdmin)

    return admin
