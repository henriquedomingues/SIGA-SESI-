from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.idUser == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.emailUser == email).first()

    def get_by_cpf(self, cpf: str) -> User | None:
        return self.db.query(User).filter(User.cpfUser == cpf).first()
