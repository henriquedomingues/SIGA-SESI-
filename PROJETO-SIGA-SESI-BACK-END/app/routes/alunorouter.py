from fastapi import APIRouter, Depends
from app.dependencies.authroutes import get_current_user  # 👈 IMPORTANTE

router = APIRouter()

@router.get("/aluno")
def aluno(user=Depends(get_current_user)):
    return {"msg": "acesso permitido", "user": user}