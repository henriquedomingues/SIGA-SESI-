from sqlalchemy import Column, Integer, String
from app.config.database import Base

class User(Base):
    __tablename__ = "tblUser"

    idUser = Column(Integer, primary_key=True)
    nomeUser = Column(String(100))
    cpfUser = Column(String(14))
    emailUser = Column(String(100))
    password = Column(String(255))
    tipoUser = Column(String(20))