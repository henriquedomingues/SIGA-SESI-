from sqladmin import ModelView
from starlette.requests import Request

from app.admin_panel.auth import ADMIN_ROLE
from app.models.matricula import Matricula
from app.models.user import User


class AdminOnlyModelView(ModelView):
    page_size = 25
    page_size_options = [25, 50, 100]

    def is_accessible(self, request: Request) -> bool:
        return request.session.get("admin_user_role") == ADMIN_ROLE

    def is_visible(self, request: Request) -> bool:
        return self.is_accessible(request)


class UserAdmin(AdminOnlyModelView, model=User):
    name = "Usuario"
    name_plural = "Usuarios"
    icon = "fa-solid fa-users"
    category = "Cadastros"

    can_create = False
    can_edit = True
    can_delete = False
    can_view_details = True
    can_export = True

    column_list = [
        User.idUser,
        User.nomeUser,
        User.cpfUser,
        User.emailUser,
        User.tipoUser,
    ]
    column_details_list = column_list
    column_searchable_list = [
        User.nomeUser,
        User.cpfUser,
        User.emailUser,
        User.tipoUser,
    ]
    column_sortable_list = [
        User.idUser,
        User.nomeUser,
        User.emailUser,
        User.tipoUser,
    ]
    column_default_sort = [(User.idUser, True)]
    column_labels = {
        User.idUser: "ID",
        User.nomeUser: "Nome",
        User.cpfUser: "CPF",
        User.emailUser: "Email",
        User.tipoUser: "Tipo",
    }

    form_excluded_columns = [User.password]


class MatriculaAdmin(AdminOnlyModelView, model=Matricula):
    name = "Matricula"
    name_plural = "Matriculas"
    icon = "fa-solid fa-id-card"
    category = "Cadastros"

    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True
    can_export = True

    column_list = [
        Matricula.idMatricula,
        Matricula.idUser,
        Matricula.idEscola,
        Matricula.rm,
        Matricula.ativo,
    ]
    column_details_list = column_list
    column_searchable_list = [
        Matricula.rm,
    ]
    column_sortable_list = [
        Matricula.idMatricula,
        Matricula.idUser,
        Matricula.idEscola,
        Matricula.rm,
        Matricula.ativo,
    ]
    column_default_sort = [(Matricula.idMatricula, True)]
    column_labels = {
        Matricula.idMatricula: "ID",
        Matricula.idUser: "Usuario",
        Matricula.idEscola: "Escola",
        Matricula.rm: "RM",
        Matricula.ativo: "Ativo",
    }
