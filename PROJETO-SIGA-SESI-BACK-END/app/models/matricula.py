from sqlalchemy import Column, Integer, String, Boolean
from app.config.database import Base

class Matricula(Base):
    __tablename__ = "tblMatricula"

    idMatricula = Column(Integer, primary_key=True)
    idUser = Column(Integer)
    idEscola = Column(Integer)
    rm = Column(String(20))
    ativo = Column(Boolean)