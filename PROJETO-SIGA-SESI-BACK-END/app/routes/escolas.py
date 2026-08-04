from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_escolas():
    return [
        {"id": 1, "nome": "ESCOLA SESI BARRETOS"}
    ]