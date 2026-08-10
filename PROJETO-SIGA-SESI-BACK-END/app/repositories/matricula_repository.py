from sqlalchemy.orm import Session

from app.models.matricula import Matricula


class MatriculaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_by_rm_and_school(
        self,
        rm: str,
        school_id: int,
    ) -> Matricula | None:
        return (
            self.db.query(Matricula)
            .filter(
                Matricula.rm == rm,
                Matricula.idEscola == school_id,
                Matricula.ativo == True,
            )
            .first()
        )

    def get_active_by_user_and_school(
        self,
        user_id: int,
        school_id: int,
    ) -> Matricula | None:
        return (
            self.db.query(Matricula)
            .filter(
                Matricula.idUser == user_id,
                Matricula.idEscola == school_id,
                Matricula.ativo == True,
            )
            .first()
        )
