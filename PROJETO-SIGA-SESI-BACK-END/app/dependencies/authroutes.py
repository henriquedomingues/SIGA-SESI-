from app.core.dependencies import get_current_user, role_required


get_current_aluno = role_required("ALUNO")

__all__ = ["get_current_user", "get_current_aluno"]
