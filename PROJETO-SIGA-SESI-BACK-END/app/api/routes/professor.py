from fastapi import APIRouter, Depends

from app.core.dependencies import role_required


router = APIRouter()


@router.get("/professor")
def rota_professor(user=Depends(role_required("PROFESSOR"))):
    return {"msg": "Bem-vindo professor"}
