from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/professor")
def rota_professor(user=Depends(role_required("PROFESSOR"))):
    return {"msg": "Bem-vindo professor"}


