from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.user_schema import LoginSchema, TokenSchema
from app.services.auth_service import AuthService


router = APIRouter()


@router.post("/login", response_model=TokenSchema)
def login(
    data: LoginSchema,
    request: Request,
    db: Session = Depends(get_db),
):
    ip_address = request.client.host if request.client else "unknown"
    return AuthService(db).login(data, ip_address)
