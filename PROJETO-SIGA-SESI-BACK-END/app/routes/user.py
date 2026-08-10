from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user


router = APIRouter()


@router.get("/perfil")
def perfil(user=Depends(get_current_user)):
    return user
