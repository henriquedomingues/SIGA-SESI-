@router.get("/perfil")
def perfil(user=Depends(get_current_user)):
    return user