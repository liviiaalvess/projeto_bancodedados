from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from database import conectar
import bcrypt
import jwt
import os

router = APIRouter()

# Força uma chave direta caso o .env não esteja sendo lido por algum motivo
SECRET_KEY = os.getenv("SECRET_KEY") or "0bf92ba639625020007dc4807130d35f3fec52e63d95019a4318864bca14c06e"
ALGORITMO = "HS256"


class Login(BaseModel):
    email: str
    senha: str


@router.post("/login")
def login(dados: Login):
    if not SECRET_KEY:
        return {"erro": "SECRET_KEY não foi configurada"}

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM usuario WHERE email = %s",
            (dados.email,),
        )
        usuario = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not usuario:
        return {"erro": "E-mail ou senha inválidos"}

    senha_confere = bcrypt.checkpw(
        dados.senha.encode("utf-8"),
        usuario["senha"].encode("utf-8"),
    )

    if not senha_confere:
        return {"erro": "E-mail ou senha inválidos"}

    expira_em = datetime.now(timezone.utc) + timedelta(hours=2)

    payload = {
        "sub": usuario["email"],
        "exp": expira_em,
    }

    if "tipo" in usuario:
        payload["tipo"] = usuario["tipo"]

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITMO,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }