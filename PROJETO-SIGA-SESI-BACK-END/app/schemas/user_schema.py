from pydantic import BaseModel
from typing import Optional

class LoginSchema(BaseModel):
    password: str
    tipoUser: str
    escolaId: int

    emailUser: Optional[str] = None
    cpfUser: Optional[str] = None
    rm: Optional[str] = None