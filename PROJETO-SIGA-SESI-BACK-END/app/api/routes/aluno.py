from fastapi import APIRouter, Depends

from app.core.dependencies import role_required


router = APIRouter()


@router.get("/aluno")
def aluno(user=Depends(role_required("ALUNO"))):
    return {"msg": "acesso permitido", "user": user}
