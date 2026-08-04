
def role_required(role: str):
    def role_checker(user=Depends(get_current_user)):
        if user.get("tipoUser") != role:
            raise HTTPException(status_code=403, detail="Acesso negado")
        return user
    return role_checker